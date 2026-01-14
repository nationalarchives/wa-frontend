import json
from datetime import datetime
from urllib.parse import unquote

from flask import request, current_app


def now_iso_8601():
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def cookie_preference(policy):
    if "cookies_policy" in request.cookies:
        cookies_policy = request.cookies["cookies_policy"]
        preferences = json.loads(unquote(cookies_policy))
        return preferences[policy] if policy in preferences else None
    return None


def get_navigation_data():
    """
    Returns navigation data structure for templates.
    This should be configured via config or database in production.
    """
    return {
        "primary": [
            {"title": "About", "url": "/about/", "page": {"id": 1, "title": "About"}},
            {
                "title": "Collections",
                "url": "/collections/",
                "page": {"id": 2, "title": "Collections"},
            },
            {"title": "Help", "url": "/help/", "page": {"id": 3, "title": "Help"}},
        ],
        "secondary": [
            {"title": "Blog", "url": "/blog/", "page": {"id": 4, "title": "Blog"}},
            {
                "title": "Contact",
                "url": "/contact/",
                "page": {"id": 5, "title": "Contact"},
            },
        ],
        "footer": [
            {
                "heading": "About",
                "links": [
                    {"title": "About us", "url": "/about/"},
                    {"title": "Our work", "url": "/about/our-work/"},
                    {"title": "Contact us", "url": "/contact/"},
                ],
            },
            {
                "heading": "Collections",
                "links": [
                    {"title": "Browse collections", "url": "/collections/"},
                    {"title": "Archive highlights", "url": "/collections/highlights/"},
                ],
            },
        ],
        "footer_links": [
            {"title": "Accessibility statement", "url": "/accessibility/"},
            {"title": "Privacy policy", "url": "/privacy/"},
            {"title": "Cookies", "url": "/cookies/"},
            {"title": "Terms of use", "url": "/terms/"},
        ],
    }


def get_social_media_data():
    """Returns social media settings."""
    return {
        "twitter_handle": current_app.config.get("TWITTER_HANDLE", ""),
        "facebook_url": current_app.config.get("FACEBOOK_URL", ""),
        "facebook_app_id": current_app.config.get("FACEBOOK_APP_ID", ""),
        "site_name": current_app.config.get("SITE_NAME", "UK Government Web Archive"),
    }


def inject_global_context():
    """Inject global context variables into all templates."""
    return {
        "navigation": get_navigation_data(),
        "social_media": get_social_media_data(),
        "config": {
            "SITE_NAME": current_app.config.get(
                "SITE_NAME", "UK Government Web Archive"
            ),
            "LANGUAGE_CODE": "en",
            "SEO_NOINDEX": current_app.config.get("SEO_NOINDEX", False),
            "GOOGLE_TAG_MANAGER_ID": current_app.config.get(
                "GOOGLE_TAG_MANAGER_ID", ""
            ),
            "BUILD_VERSION": current_app.config.get("BUILD_VERSION", "1.0.0"),
            "COOKIE_DOMAIN": current_app.config.get("COOKIE_DOMAIN", ""),
        },
        "ancestor_ids": [],  # Can be populated based on current page context
    }
