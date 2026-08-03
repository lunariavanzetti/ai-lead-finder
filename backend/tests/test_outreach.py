from app.services.outreach import (
    build_discovery_questions,
    build_followup_message,
    build_outreach_message,
    build_strengths,
)


def test_outreach_message_picks_one_specific_gap_not_a_list():
    pain_points = [
        {"code": "chatbot", "label": "No chatbot", "severity": "high"},
        {"code": "booking_system", "label": "No online booking", "severity": "high"},
        {"code": "ssl", "label": "Missing SSL", "severity": "high"},
    ]
    message = build_outreach_message(
        "Bright Smile Dental", "Dentist", pain_points, 4.8, 120, "Dr. Jane Smith",
    )
    assert message.startswith("Hi Jane,")
    assert "Bright Smile Dental" in message
    # Leads with ONE concrete observation (booking_system wins by priority),
    # not a dump of every detected flaw.
    assert message.count("I noticed") == 1
    assert "book" in message.lower()
    assert "chatbot" not in message.lower()
    assert "ssl" not in message.lower()


def test_outreach_message_no_website_uses_dedicated_template():
    pain_points = [{"code": "no_website", "label": "No website found", "severity": "high"}]
    message = build_outreach_message("Joe's Plumbing", "Plumbing", pain_points, None, None, None)
    assert message.startswith("Hi,")
    assert "doesn't have a website" in message


def test_outreach_message_clean_site_falls_back_gracefully():
    message = build_outreach_message("Acme Dental", "Dentist", [], 4.9, 50, None)
    assert "Acme Dental" in message
    assert "quick chat" in message


def test_followup_message_is_short_and_low_pressure():
    message = build_followup_message("Bright Smile Dental", "Dr. Jane Smith")
    assert message.startswith("Hi Jane,")
    assert "no strings attached" in message


def test_discovery_questions_include_pain_specific_items():
    pain_points = [{"code": "google_reviews_widget", "label": "No review automation", "severity": "medium"}]
    questions = build_discovery_questions(pain_points)
    assert any("review" in q.lower() for q in questions)
    assert len(questions) <= 5


def test_strengths_reflect_detected_technologies_only():
    technologies = {"ssl": True, "mobile_friendly": True, "chatbot": False, "booking_system": False}
    strengths = build_strengths(technologies, has_contact_form=True, google_rating=4.8, google_reviews_count=50)
    assert "Website has a valid SSL certificate" in strengths
    assert "Website is mobile-friendly" in strengths
    assert "Has an online contact form" in strengths
    assert not any("chatbot" in s.lower() for s in strengths)
