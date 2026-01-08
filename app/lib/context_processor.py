import json
from datetime import datetime
from urllib.parse import unquote

from flask import current_app, request


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


def get_social_media_data():
    """Returns social media settings."""
    return {
        "twitter_handle": current_app.config.get("TWITTER_HANDLE", ""),
        "facebook_url": current_app.config.get("FACEBOOK_URL", ""),
        "facebook_app_id": current_app.config.get("FACEBOOK_APP_ID", ""),
        "site_name": current_app.config.get("SITE_NAME", "UK Government Web Archive"),
    }
