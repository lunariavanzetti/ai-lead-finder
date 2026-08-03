"""A small pool of common, real browser user-agent strings for rotation.

Rotation here is about not hammering every target with an identical UA
fingerprint across thousands of requests — it is NOT used to impersonate a
crawler like Googlebot or to defeat bot-detection. When a site presents a
CAPTCHA or bot-check page, the crawler backs off rather than trying harder to
look human.
"""

DESKTOP_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]


def pick_user_agent(index: int, rotate: bool, fallback: str) -> str:
    if not rotate:
        return fallback
    return DESKTOP_USER_AGENTS[index % len(DESKTOP_USER_AGENTS)]
