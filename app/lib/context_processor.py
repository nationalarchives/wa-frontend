import json
from datetime import datetime, timezone
from urllib.parse import unquote

from flask import current_app, request


def now_iso_8601():
    now = datetime.now(tz=timezone.utc)
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def cookie_preferences(policy):
    if "cookie_preferences" in request.cookies:
        cookie_preferences = request.cookies["cookie_preferences"]
        preferences = json.loads(unquote(cookie_preferences))
        return preferences.get(policy, None)
    return None


def get_social_media_data():
    """Returns social media settings."""
    return {
        "twitter_handle": current_app.config.get("TWITTER_HANDLE", ""),
        "facebook_url": current_app.config.get("FACEBOOK_URL", ""),
        "facebook_app_id": current_app.config.get("FACEBOOK_APP_ID", ""),
        "site_name": current_app.config.get("SITE_NAME", "UK Government Web Archive"),
    }
