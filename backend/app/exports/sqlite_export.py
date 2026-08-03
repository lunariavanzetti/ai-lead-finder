import json
import sqlite3
from pathlib import Path

from app.models.lead import Lead


def export_sqlite(leads: list[Lead], out_path: Path) -> Path:
    if out_path.exists():
        out_path.unlink()

    conn = sqlite3.connect(out_path)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE leads (
            id TEXT PRIMARY KEY, lead_score INTEGER, business_name TEXT, business_type TEXT,
            website TEXT, phone TEXT, email TEXT, address TEXT, city TEXT, state TEXT, country TEXT,
            google_rating REAL, google_reviews_count INTEGER, facebook_url TEXT, instagram_url TEXT,
            linkedin_company_url TEXT, booking_link TEXT, has_contact_form INTEGER,
            technologies_json TEXT, pain_points_json TEXT, recommended_services_json TEXT,
            strengths_json TEXT, outreach_message TEXT, follow_up_message TEXT, discovery_questions_json TEXT,
            estimated_hours_saved_per_week REAL, status TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE staff (
            id TEXT PRIMARY KEY, lead_id TEXT, full_name TEXT, title TEXT, email TEXT,
            linkedin_url TEXT, is_decision_maker INTEGER, priority_rank INTEGER,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
        """
    )

    for lead in leads:
        cur.execute(
            """
            INSERT INTO leads VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                lead.id, lead.lead_score, lead.business_name, lead.business_type, lead.website,
                lead.phone, lead.email, lead.address, lead.city, lead.state, lead.country,
                lead.google_rating, lead.google_reviews_count, lead.facebook_url, lead.instagram_url,
                lead.linkedin_company_url, lead.booking_link, int(lead.has_contact_form),
                json.dumps(lead.technologies), json.dumps(lead.pain_points),
                json.dumps(lead.recommended_services), json.dumps(lead.strengths),
                lead.outreach_message, lead.follow_up_message, json.dumps(lead.discovery_questions),
                lead.estimated_hours_saved_per_week, lead.status,
            ),
        )
        for staff in lead.staff:
            cur.execute(
                "INSERT INTO staff VALUES (?,?,?,?,?,?,?,?)",
                (
                    staff.id, lead.id, staff.full_name, staff.title, staff.email,
                    staff.linkedin_url, int(staff.is_decision_maker), staff.priority_rank,
                ),
            )

    conn.commit()
    conn.close()
    return out_path
