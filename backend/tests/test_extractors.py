from app.extractors.contact_info import extract_address, extract_emails, extract_phones, has_contact_form, is_role_based_email
from app.extractors.social_links import extract_social_links
from app.extractors.staff_extractor import extract_staff_members
from app.extractors.tech_detector import detect_technologies

SAMPLE_HOME_HTML = """
<html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://www.googletagmanager.com/gtag/js"></script>
</head>
<body>
  <a href="mailto:info@brightsmile.com">Email us</a>
  <a href="tel:+13125551234">(312) 555-1234</a>
  <a href="https://facebook.com/brightsmile">Facebook</a>
  <a href="https://instagram.com/brightsmile">Instagram</a>
  <a href="https://linkedin.com/company/brightsmile">LinkedIn</a>
  <address>123 Main St, Chicago, IL</address>
</body></html>
"""

SAMPLE_STAFF_HTML = """
<html><body>
  <div class="team-member">
    <h3>Dr. Jane Smith</h3>
    <p class="title">Owner &amp; Lead Dentist</p>
    <a href="mailto:jane@brightsmile.com">jane@brightsmile.com</a>
  </div>
  <div class="team-member">
    <h3>John Reyes</h3>
    <p class="title">Office Manager</p>
  </div>
</body></html>
"""


def test_extract_emails_from_mailto_and_text():
    emails = extract_emails(SAMPLE_HOME_HTML)
    assert "info@brightsmile.com" in emails


def test_extract_emails_ignores_sentry_ingest_subdomains():
    html = "<html><body>bounce: a1b2c3@o1069899.ingest.sentry.io</body></html>"
    assert extract_emails(html) == []


def test_role_based_email_detection():
    assert is_role_based_email("info@brightsmile.com")
    assert not is_role_based_email("jane@brightsmile.com")


def test_extract_phones_from_tel_link():
    phones = extract_phones(SAMPLE_HOME_HTML)
    assert any("312" in p for p in phones)


def test_extract_address():
    address = extract_address(SAMPLE_HOME_HTML)
    assert address and "Chicago" in address


def test_extract_social_links():
    social = extract_social_links(SAMPLE_HOME_HTML)
    assert social["facebook_url"] == "https://facebook.com/brightsmile"
    assert social["instagram_url"] == "https://instagram.com/brightsmile"
    assert social["linkedin_company_url"] == "https://linkedin.com/company/brightsmile"


def test_detect_technologies_google_analytics():
    tech = detect_technologies(SAMPLE_HOME_HTML, "https://brightsmile.com", load_time_ms=500)
    assert tech["google_analytics"] is True
    assert tech["ssl"] is True
    assert tech["mobile_friendly"] is True
    assert tech["chatbot"] is False


def test_has_contact_form_false_without_form():
    assert has_contact_form(SAMPLE_HOME_HTML) is False


def test_extract_staff_members_rejects_section_headings_that_look_titlecase():
    html = """
    <html><body>
      <h2>Our Core Values</h2>
      <h3>Advanced Training</h3>
      <h3>Meet Your Dentists</h3>
      <h4>Quick Links</h4>
      <h3>What Sets Optima Apart</h3>
      <h3>Use Saved Payment Method</h3>
      <h2>Personalized Recommendations</h2>
      <h3>West Davis Smile Plan</h3>
      <h3>The Practice Story</h3>
    </body></html>
    """
    staff = extract_staff_members(html)
    assert staff == []


def test_extract_staff_members_rejects_titlecase_phrases_with_no_supporting_evidence():
    # These clear the word-blocklist (no obviously-generic word in them) but
    # have no title, email, LinkedIn link, or staff-card container nearby —
    # exactly the shape of real marketing copy seen in the wild.
    html = """
    <html><body>
      <h3>Home Life</h3>
      <h3>Get Started Today</h3>
      <h3>Root Canal Treatment</h3>
      <h3>Affiliate Success</h3>
      <h3>Main Navigation</h3>
    </body></html>
    """
    staff = extract_staff_members(html)
    assert staff == []


def test_extract_staff_members_keeps_name_with_title_keyword_nearby():
    html = """
    <html><body>
      <div>
        <h3>Sarmila Shrestha</h3>
        <p>Dentist</p>
      </div>
    </body></html>
    """
    staff = extract_staff_members(html)
    assert len(staff) == 1
    assert staff[0].full_name == "Sarmila Shrestha"


def test_extract_staff_members_strips_meet_prefix():
    html = "<html><body><h3>Meet Dr. Julio Obando</h3></body></html>"
    staff = extract_staff_members(html)
    assert len(staff) == 1
    assert staff[0].full_name == "Dr. Julio Obando"


def test_extract_staff_members():
    staff = extract_staff_members(SAMPLE_STAFF_HTML)
    names = [s.full_name for s in staff]
    assert "Dr. Jane Smith" in names
    jane = next(s for s in staff if s.full_name == "Dr. Jane Smith")
    assert jane.title == "Owner & Lead Dentist"
    assert jane.email == "jane@brightsmile.com"
