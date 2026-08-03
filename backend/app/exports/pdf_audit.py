from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.exports.common import primary_contact_for
from app.models.lead import Lead

BRAND = colors.HexColor("#4F46E5")
DARK = colors.HexColor("#111827")
MUTED = colors.HexColor("#6B7280")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("AuditTitle", fontSize=22, leading=26, textColor=DARK, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("AuditSubtitle", fontSize=12, leading=16, textColor=MUTED))
    styles.add(ParagraphStyle("SectionHeading", fontSize=13, leading=18, textColor=BRAND, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle("Body", fontSize=10.5, leading=15, textColor=DARK))
    styles.add(ParagraphStyle("ScoreBig", fontSize=36, leading=40, textColor=BRAND, fontName="Helvetica-Bold"))
    return styles


def generate_audit_pdf(lead: Lead, out_path: Path) -> Path:
    styles = _styles()
    doc = SimpleDocTemplate(
        str(out_path), pagesize=LETTER,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    )
    story = []

    story.append(Paragraph("AI Automation Audit", styles["AuditTitle"]))
    story.append(Paragraph(escape(lead.business_name), styles["AuditSubtitle"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#E5E7EB"), thickness=1))
    story.append(Spacer(1, 14))

    contact = primary_contact_for(lead)
    decision_maker_value = "-"
    if contact:
        decision_maker_value = escape(f"{contact.full_name} ({contact.title})" if contact.title else contact.full_name)

    info_rows = [
        ["Business Type", escape(lead.business_type or "-")],
        ["Website", escape(lead.website or "-")],
        ["Phone", escape(lead.phone or "-")],
        ["Email", escape(lead.email or "-")],
        ["Address", escape(", ".join(filter(None, [lead.address, lead.city, lead.state, lead.country])) or "-")],
        ["Decision Maker", decision_maker_value],
        ["Google Rating", escape(f"{lead.google_rating} ({lead.google_reviews_count} reviews)" if lead.google_rating else "-")],
    ]
    if contact and contact.linkedin_url:
        info_rows.append(["LinkedIn", escape(contact.linkedin_url)])

    info_table = Table(info_rows, colWidths=[1.6 * inch, 4.6 * inch])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
                ("TEXTCOLOR", (1, 0), (1, -1), DARK),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(info_table)

    story.append(Paragraph("Lead / Opportunity Score", styles["SectionHeading"]))
    story.append(Paragraph(f"{lead.lead_score} / 100", styles["ScoreBig"]))
    story.append(Spacer(1, 6))

    if lead.strengths:
        story.append(Paragraph("Strengths", styles["SectionHeading"]))
        for strength in lead.strengths:
            story.append(Paragraph(f"&#10003;&nbsp;&nbsp;{escape(strength)}", styles["Body"]))

    story.append(Paragraph("Detected Problems", styles["SectionHeading"]))
    if lead.pain_points:
        for point in lead.pain_points:
            story.append(Paragraph(f"&#10007;&nbsp;&nbsp;{escape(point.get('label', ''))}", styles["Body"]))
    else:
        story.append(Paragraph("No significant gaps detected.", styles["Body"]))

    story.append(Paragraph("Recommended Solutions", styles["SectionHeading"]))
    if lead.recommended_services:
        for service in lead.recommended_services:
            story.append(Paragraph(f"&#8226;&nbsp;&nbsp;{escape(service)}", styles["Body"]))
    else:
        story.append(Paragraph("No specific recommendations at this time.", styles["Body"]))

    if lead.estimated_hours_saved_per_week:
        story.append(Paragraph("Estimated Time Saved", styles["SectionHeading"]))
        story.append(Paragraph(f"~{lead.estimated_hours_saved_per_week} hours / week", styles["Body"]))

    if lead.outreach_message:
        story.append(Paragraph("Suggested Outreach Message", styles["SectionHeading"]))
        story.append(Paragraph(escape(lead.outreach_message), styles["Body"]))

    if lead.follow_up_message:
        story.append(Paragraph("Suggested Follow-Up Message", styles["SectionHeading"]))
        story.append(Paragraph(escape(lead.follow_up_message), styles["Body"]))

    if lead.discovery_questions:
        story.append(Paragraph("Discovery Call Questions", styles["SectionHeading"]))
        for question in lead.discovery_questions:
            story.append(Paragraph(f"&#8226;&nbsp;&nbsp;{escape(question)}", styles["Body"]))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#E5E7EB"), thickness=1))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Generated by AI Lead Finder from publicly available business information. "
            "Figures are heuristic estimates, not guarantees.",
            styles["AuditSubtitle"],
        )
    )

    doc.build(story)
    return out_path
