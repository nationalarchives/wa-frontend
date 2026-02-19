from urllib.parse import unquote

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


def page_details(page_id, params={}):
    uri = f"pages/{page_id}/"
    params = params | {
        "include_aliases": "",
    }
    return wagtail_request_handler(uri, params)


def page_details_by_uri(page_uri, params={}):
    uri = "pages/find/"
    params = params | {
        "html_path": page_uri,
        "include_aliases": "",
    }
    return wagtail_request_handler(uri, params)


def page_preview(content_type, token, params={}):
    uri = "page_preview/1/"
    params = params | {"content_type": content_type, "token": token}
    return wagtail_request_handler(uri, params)


def image(image_uuid, params={}):
    uri = f"images/{image_uuid}/"
    return wagtail_request_handler(uri, params)


def redirect_by_uri(path, params={}):
    uri = "redirects/find/"
    params = params | {
        "html_path": unquote(path),
    }
    return wagtail_request_handler(uri, params)


def page_children(page_id, params={}, limit=None):
    if not page_id:
        return {}
    uri = "pages/"
    params = params | {
        "child_of": page_id,
        "limit": limit or current_app.config.get("WAGTAILAPI_LIMIT_MAX"),
        "include_aliases": "",
    }
    return wagtail_request_handler(uri, params)


def pages_paginated(
    page,
    limit=None,
    initial_offset=0,
    params={},
):
    if not limit:
        limit = current_app.config.get("WAGTAILAPI_LIMIT_MAX")
    offset = ((page - 1) * limit) + initial_offset
    uri = "pages/"
    params = params | {
        "offset": offset,
        "limit": limit,
    }
    return wagtail_request_handler(uri, params)


def page_children_paginated(
    page_id,
    page,
    limit=None,
    initial_offset=0,
    params={},
):
    if not page_id:
        return {"items": [], "meta": {"total_count": 0}}
    return pages_paginated(
        page=page,
        limit=limit,
        initial_offset=initial_offset,
        params=params
        | {
            "child_of": page_id,
        },
    )


def _get_navigation_cache_key():
    """Generate cache key for navigation settings."""
    site = current_app.config.get("WAGTAIL_SITE_HOSTNAME", "default")
    return f"navigation_settings:{site}:v1"


@cache.cached(
    key_prefix=_get_navigation_cache_key,
)
def navigation_settings():
    """
    Get navigation settings from the API with caching via Flask-Caching package.
    """
    try:
        return wagtail_request_handler("globals/navigation/")
    except Exception as e:
        current_app.logger.error(f"Failed to get navigation settings: {e}")
        return {}
