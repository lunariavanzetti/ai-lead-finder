"""Per-business pipeline: crawl -> extract -> score. Kept separate from the
orchestrator so it can be unit-tested (and reused by a future "re-analyze
this single lead" endpoint) without spinning up a whole job."""

from app.discovery.google_custom_search import GoogleCustomSearchClient
from app.discovery.schemas import DiscoveredBusiness
from app.extractors.contact_info import (
    extract_address,
    extract_emails,
    extract_phones,
    has_contact_form,
    is_role_based_email,
)
from app.extractors.social_links import extract_social_links
from app.extractors.staff_extractor import extract_staff_members
from app.extractors.tech_detector import detect_technologies
from app.scoring.decision_maker import primary_contact, rank_staff
from app.scoring.lead_score import calculate_lead_score
from app.scoring.pain_points import generate_pain_points
from app.scoring.recommendations import estimate_hours_saved, recommend_services
from app.scrapers.fetcher import CrawlConfig
from app.scrapers.site_crawler import SiteCrawler
from app.services.outreach import (
    build_discovery_questions,
    build_followup_message,
    build_outreach_message,
    build_strengths,
)


def _classify_business_type(user_supplied_type: str, raw_text: str) -> str:
    """The user already tells us the business type via the search form (it
    drove the discovery query), so we trust and normalize that rather than
    re-guessing it from page text — the form input is the ground truth here."""
    return user_supplied_type.strip().title()


def _is_eu_uk_country(country: str | None) -> bool:
    if not country:
        return False
    eu_uk = {
        "united kingdom", "uk", "ireland", "germany", "france", "spain", "italy",
        "netherlands", "belgium", "austria", "portugal", "sweden", "denmark",
        "finland", "poland", "greece", "czech republic", "hungary", "romania",
        "bulgaria", "croatia", "slovakia", "slovenia", "estonia", "latvia",
        "lithuania", "luxembourg", "malta", "cyprus",
    }
    return country.strip().lower() in eu_uk


def build_base_result(business: DiscoveredBusiness, business_type: str) -> dict:
    """Default-valued lead record shared by the happy path and every error
    path, so a failed/partial crawl still yields a fully-shaped row."""
    return {
        "business_name": business.business_name,
        "business_type": _classify_business_type(business_type, ""),
        "website": business.website,
        "phone": business.phone,
        "email": None,
        "address": business.address,
        "city": business.city,
        "state": business.state,
        "country": business.country,
        "google_place_id": business.google_place_id,
        "google_maps_url": business.google_maps_url,
        "google_rating": business.google_rating,
        "google_reviews_count": business.google_reviews_count,
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_company_url": None,
        "whatsapp_detected": False,
        "messenger_detected": False,
        "booking_link": None,
        "has_contact_form": False,
        "has_staff_page": False,
        "has_about_page": False,
        "technologies": {},
        "pain_points": [],
        "recommended_services": [],
        "lead_score": 0,
        "score_breakdown": {},
        "estimated_hours_saved_per_week": None,
        "strengths": [],
        "outreach_message": None,
        "follow_up_message": None,
        "discovery_questions": [],
        "screenshot_path": None,
        "staff": [],
        "crawl_error": None,
    }


def build_error_result(business: DiscoveredBusiness, business_type: str, error_message: str) -> dict:
    result = build_base_result(business, business_type)
    result["crawl_error"] = error_message
    result["pain_points"] = [{"code": "processing_error", "label": "Could not be fully analyzed", "severity": "low"}]
    score, breakdown = calculate_lead_score(
        result["pain_points"], has_decision_maker=False, has_email=False, has_phone=bool(business.phone),
    )
    result["lead_score"] = score
    result["score_breakdown"] = breakdown
    return result


async def process_business(
    business: DiscoveredBusiness,
    business_type: str,
    decision_maker_titles: list[str],
    crawl_config: CrawlConfig,
    exclude_personal_data_eu: bool,
    capture_screenshot: bool = False,
    screenshot_path: str | None = None,
    find_decision_maker_linkedin: bool = True,
) -> dict:
    result = build_base_result(business, business_type)

    if not business.website:
        result["pain_points"] = [
            {"code": "no_website", "label": "No website found", "severity": "high"}
        ]
        result["recommended_services"] = ["AI Receptionist", "Lead Qualification"]
        result["estimated_hours_saved_per_week"] = estimate_hours_saved(result["recommended_services"])
        result["outreach_message"] = build_outreach_message(
            business.business_name, business_type, result["pain_points"], None, None, None,
        )
        result["follow_up_message"] = build_followup_message(business.business_name, None)
        result["discovery_questions"] = build_discovery_questions(result["pain_points"])
        score, breakdown = calculate_lead_score(
            result["pain_points"], has_decision_maker=False,
            has_email=False, has_phone=bool(business.phone),
        )
        result["lead_score"] = score
        result["score_breakdown"] = breakdown
        return result

    crawler = SiteCrawler(crawl_config)
    bundle = await crawler.crawl(
        business.website,
        capture_screenshot=capture_screenshot,
        screenshot_path=screenshot_path,
    )

    if bundle.blocked or not bundle.homepage_html:
        result["crawl_error"] = bundle.error or "unreachable"
        result["pain_points"] = [
            {"code": "unreachable", "label": "Website unreachable during scan", "severity": "medium"}
        ]
        score, breakdown = calculate_lead_score(
            result["pain_points"], has_decision_maker=False,
            has_email=False, has_phone=bool(business.phone),
        )
        result["lead_score"] = score
        result["score_breakdown"] = breakdown
        return result

    combined_html_for_contact = bundle.homepage_html + (bundle.contact_html or "")
    emails = extract_emails(combined_html_for_contact)
    is_eu = exclude_personal_data_eu and _is_eu_uk_country(business.country)
    if is_eu:
        emails = [e for e in emails if is_role_based_email(e)]

    phones = extract_phones(combined_html_for_contact)
    address = extract_address(combined_html_for_contact) or business.address

    social = extract_social_links(bundle.homepage_html + (bundle.contact_html or ""))
    technologies = detect_technologies(bundle.homepage_html, business.website, bundle.load_time_ms)
    contact_form_present = has_contact_form(bundle.contact_html or bundle.homepage_html)

    staff_members = []
    if bundle.staff_html:
        raw_staff = extract_staff_members(bundle.staff_html)
        staff_members = rank_staff(raw_staff, decision_maker_titles)
        if is_eu:
            for member in staff_members:
                if member.get("email") and not is_role_based_email(member["email"]):
                    member["email"] = None

    pain_points = generate_pain_points(
        technologies=technologies,
        has_contact_form=contact_form_present,
        booking_link=bundle.booking_link,
        business_type=business_type,
    )
    recommended = recommend_services(pain_points)
    hours_saved = estimate_hours_saved(recommended)

    top_contact = primary_contact(staff_members)
    has_decision_maker = bool(top_contact and top_contact["is_decision_maker"])

    # The site crawl already captures a staff member's LinkedIn if their own
    # team page links to it. Only fall back to a Google Custom Search lookup
    # (official API, never visits LinkedIn) when that's missing.
    if find_decision_maker_linkedin and top_contact and not top_contact.get("linkedin_url"):
        custom_search = GoogleCustomSearchClient()
        found_url = await custom_search.find_person_linkedin(top_contact["full_name"], business.business_name)
        if found_url:
            top_contact["linkedin_url"] = found_url

    primary_email = emails[0] if emails else (top_contact["email"] if top_contact else None)
    primary_phone = phones[0] if phones else business.phone

    score, breakdown = calculate_lead_score(
        pain_points,
        has_decision_maker=has_decision_maker,
        has_email=bool(primary_email),
        has_phone=bool(primary_phone),
    )

    contact_name = top_contact["full_name"] if top_contact else None
    strengths = build_strengths(technologies, contact_form_present, business.google_rating, business.google_reviews_count)
    outreach_message = build_outreach_message(
        business.business_name, business_type, pain_points,
        business.google_rating, business.google_reviews_count, contact_name,
    )
    follow_up_message = build_followup_message(business.business_name, contact_name)
    discovery_questions = build_discovery_questions(pain_points)

    result.update(
        {
            "email": primary_email,
            "phone": primary_phone or business.phone,
            "address": address,
            "facebook_url": social["facebook_url"],
            "instagram_url": social["instagram_url"],
            "linkedin_company_url": social["linkedin_company_url"],
            "whatsapp_detected": social["whatsapp_detected"],
            "messenger_detected": social["messenger_detected"],
            "booking_link": bundle.booking_link,
            "has_contact_form": contact_form_present,
            "has_staff_page": bool(bundle.staff_html),
            "has_about_page": bool(bundle.about_html),
            "technologies": technologies,
            "pain_points": pain_points,
            "recommended_services": recommended,
            "lead_score": score,
            "score_breakdown": breakdown,
            "estimated_hours_saved_per_week": hours_saved,
            "strengths": strengths,
            "outreach_message": outreach_message,
            "follow_up_message": follow_up_message,
            "discovery_questions": discovery_questions,
            "screenshot_path": bundle.screenshot_path,
            "staff": staff_members,
        }
    )
    return result
