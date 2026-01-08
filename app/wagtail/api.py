from app.lib.api import JSONAPIClient
from app.lib.cache import cache
from flask import current_app


def wagtail_request_handler(uri, params={}):
    api_url = current_app.config.get("WAGTAIL_API_URL")
    if not api_url:
        current_app.logger.critical("WAGTAIL_API_URL not set")
        raise Exception("WAGTAIL_API_URL not set")
    client = JSONAPIClient(api_url)
    client.add_parameter("format", "json")
    if site_hostname := current_app.config.get("WAGTAIL_SITE_HOSTNAME"):
        client.add_parameter("site", site_hostname)
    client.add_parameters(params)
    data = client.get(uri)
    return data


def navigation_settings():
    """
    Get navigation settings from the API with caching via Flask-Caching.

    Cache duration is configured via NAVIGATION_CACHE_TTL (default: 900 seconds / 15 minutes).
    Falls back to direct API call if cache is unavailable.
    """
    cache_key = "navigation_settings:v1"

    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        current_app.logger.debug("Navigation settings retrieved from cache")
        return cached_data

    # Fetch from API
    try:
        navigation_data = wagtail_request_handler("globals/navigation/")

        # Cache the result with custom TTL
        ttl = current_app.config.get("NAVIGATION_CACHE_TTL", 900)
        cache.set(cache_key, navigation_data, timeout=ttl)
        current_app.logger.debug(f"Navigation settings cached for {ttl} seconds")

        return navigation_data
    except Exception as e:
        current_app.logger.error(f"Failed to get navigation settings: {e}")
        return {}
