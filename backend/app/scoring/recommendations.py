PAIN_POINT_TO_SERVICE = {
    "chatbot": "FAQ Bot",
    "live_chat": "AI Receptionist",
    "booking_system": "Appointment Reminder",
    "reminders": "Appointment Reminder",
    "faq": "FAQ Bot",
    "contact_form": "Lead Qualification",
    "google_reviews_widget": "Review Automation",
    "ai_receptionist": "AI Receptionist",
    "mobile_friendly": "CRM Automation",
}

# Rough, conservative hours-saved-per-week estimate per recommended service —
# a heuristic for the audit, not a guarantee.
SERVICE_HOURS_SAVED = {
    "AI Receptionist": 6.0,
    "Lead Qualification": 3.0,
    "Appointment Reminder": 2.5,
    "Review Automation": 1.5,
    "Email Automation": 2.0,
    "CRM Automation": 3.0,
    "SMS Follow-up": 2.0,
    "FAQ Bot": 2.0,
    "Voice Agent": 5.0,
}


def recommend_services(pain_points: list[dict]) -> list[str]:
    services: list[str] = []
    for point in pain_points:
        service = PAIN_POINT_TO_SERVICE.get(point["code"])
        if service and service not in services:
            services.append(service)
    return services


def estimate_hours_saved(recommended_services: list[str]) -> float:
    return round(sum(SERVICE_HOURS_SAVED.get(s, 0) for s in recommended_services), 1)
