from app.extractors.staff_extractor import ExtractedStaffMember
from app.scoring.decision_maker import primary_contact, rank_staff
from app.scoring.lead_score import calculate_lead_score
from app.scoring.pain_points import generate_pain_points
from app.scoring.recommendations import estimate_hours_saved, recommend_services


def test_rank_staff_identifies_decision_maker():
    staff = [
        ExtractedStaffMember(full_name="John Reyes", title="Office Manager", email=None, linkedin_url=None),
        ExtractedStaffMember(full_name="Jane Smith", title="Owner & Lead Dentist", email="jane@x.com", linkedin_url=None),
        ExtractedStaffMember(full_name="Sam Lee", title="Receptionist", email=None, linkedin_url=None),
    ]
    ranked = rank_staff(staff, selected_decision_maker_titles=["Owner", "Founder", "Office Manager"])

    assert ranked[0]["full_name"] == "Jane Smith"  # owner ranks highest priority
    assert ranked[0]["is_decision_maker"] is True

    top = primary_contact(ranked)
    assert top["full_name"] == "Jane Smith"


def test_rank_staff_no_match_falls_back_to_top_ranked():
    staff = [ExtractedStaffMember(full_name="Sam Lee", title="Receptionist", email=None, linkedin_url=None)]
    ranked = rank_staff(staff, selected_decision_maker_titles=["Owner"])
    assert ranked[0]["is_decision_maker"] is False
    assert primary_contact(ranked)["full_name"] == "Sam Lee"


def test_generate_pain_points_flags_missing_essentials():
    technologies = {
        "chatbot": False, "live_chat": False, "booking_system": False,
        "faq": False, "is_slow": False, "ssl": False, "mobile_friendly": True,
        "google_reviews_widget": False,
    }
    points = generate_pain_points(technologies, has_contact_form=False, booking_link=None, business_type="Dentist")
    codes = {p["code"] for p in points}
    assert "chatbot" in codes
    assert "booking_system" in codes
    assert "ssl" in codes

    dental_label = next(p["label"] for p in points if p["code"] == "booking_system")
    assert dental_label == "No online appointment booking"


def test_generate_pain_points_clean_site_has_fewer_gaps():
    technologies = {
        "chatbot": True, "live_chat": True, "booking_system": True,
        "faq": True, "is_slow": False, "ssl": True, "mobile_friendly": True,
        "google_reviews_widget": True,
    }
    points = generate_pain_points(technologies, has_contact_form=True, booking_link="https://calendly.com/x", business_type="Dentist")
    codes = {p["code"] for p in points}
    assert "chatbot" not in codes
    assert "booking_system" not in codes
    assert "ssl" not in codes


def test_lead_score_increases_with_more_pain_points_and_contactability():
    few_points = [{"code": "faq", "label": "No FAQ", "severity": "low"}]
    many_points = [
        {"code": "chatbot", "label": "No chatbot", "severity": "high"},
        {"code": "booking_system", "label": "No booking", "severity": "high"},
        {"code": "ssl", "label": "No SSL", "severity": "high"},
    ]

    low_score, _ = calculate_lead_score(few_points, has_decision_maker=False, has_email=False, has_phone=False)
    high_score, breakdown = calculate_lead_score(many_points, has_decision_maker=True, has_email=True, has_phone=True)

    assert high_score > low_score
    assert 0 <= high_score <= 100
    assert breakdown["total"] == high_score


def test_recommendations_and_hours_saved():
    pain_points = [
        {"code": "chatbot", "label": "No chatbot", "severity": "high"},
        {"code": "booking_system", "label": "No booking", "severity": "high"},
    ]
    services = recommend_services(pain_points)
    assert "FAQ Bot" in services
    assert "Appointment Reminder" in services

    hours = estimate_hours_saved(services)
    assert hours > 0
