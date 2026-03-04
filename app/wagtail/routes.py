from urllib.parse import quote, quote_plus, unquote, urlparse

from app.lib.api import ResourceForbidden, ResourceNotFound
from app.wagtail import bp
from app.wagtail.constants import (
    SOCIAL_SEARCH_BASE,
    WEB_KEYWORD_SEARCH_BASE,
    WEB_SITE_SEARCH_BASE,
    ArchiveType,
    SearchType,
)
from app.wagtail.render import render_content_page
from flask import (
    current_app,
    redirect,
    render_template,
    request,
    url_for,
)
from pydash import objects

from .api import (
    image,
    page_details,
    page_details_by_uri,
    page_preview,
    redirect_by_uri,
)


@bp.route("/preview/")
def preview_page():
    content_type = request.args.get("content_type")
    token = request.args.get("token")
    if not content_type or not token:
        return render_template("errors/page-not-found.html"), 404
    try:
        page_data = page_preview(content_type, token)
    except ResourceNotFound:
        return render_template("errors/page-not-found.html"), 404
    except ResourceForbidden:
        return render_template("errors/forbidden.html"), 403
    except Exception as e:
        current_app.logger.error(f"Failed to get page preview data: {e}")
        return render_template("errors/api.html"), 502
    try:
        return render_content_page(
            page_data | {"page_preview": True, "id": objects.get(page_data, "id", 0)}
        )
    except Exception as e:
        current_app.logger.error(f"Failed to render page preview: {e}")
        return render_template("errors/api.html"), 502


@bp.route("/preview/<int:page_id>/", methods=["GET", "POST"])
def preview_protected_page(page_id):
    """
    Renders a preview of a Wagtail page that is password protected.
    """

    try:
        # Get the page details from Wagtail by its id and include the provided password
        password = objects.get(request.form, "password", "")
        params = {"password": password}
        page_data = page_details(
            page_id=page_id,
            params=params,
        )
    except ResourceNotFound:
        return render_template("errors/page-not-found.html"), 404
    except ResourceForbidden:
        return render_template("errors/forbidden.html"), 403
    except Exception as e:
        current_app.logger.error(f"Failed to render page preview: {e}")
        return render_template("errors/api.html"), 502

    # Check if the page is password protected
    if objects.get(page_data, "meta.privacy") == "password":
        # If meta.locked is True then the page is still locked which means the password
        # is not correct
        if objects.get(page_data, "meta.locked"):
            if request.method == "POST" and "password" in request.form:
                if request.form["password"] == "":
                    page_data["error"] = "Enter a password"
                else:
                    page_data["error"] = "Incorrect password"

            # Render the password protected page template
            return render_template(
                "errors/password_protected.html",
                page_data=page_data,
            )

        # If the page is not password protected, render the protected page
        return render_content_page(page_data)

    # If the page is no longer password protected, redirect to the main page URL
    if url := objects.get(page_data, "meta.url"):
        return redirect(url, code=302)

    return render_template("errors/api.html"), 502


@bp.route("/page/<int:page_id>/")
def page_permalink(page_id):
    """
    Redirects to the Wagtail page by its ID, if it exists, acting as a permalink.
    """

    try:
        # Get the page details from Wagtail by its ID
        page_data = page_details(page_id)
    except ResourceNotFound:
        return render_template("errors/page-not-found.html"), 404
    except ResourceForbidden:
        return render_template("errors/forbidden.html"), 403
    except Exception as e:
        current_app.logger.error(f"Failed to get page details: {e}")
        return render_template("errors/api.html"), 502

    # If the page has a URL, redirect to it
    if url := objects.get(page_data, "meta.url"):
        return redirect(url, code=302)

    # If the page does not have a URL, log an error and return a 502 error page
    current_app.logger.error(f"Cannot generate permalink for page: {page_id}")
    return render_template("errors/api.html"), 502


@bp.route("/", defaults={"path": "/"})
@bp.route("/<path:path>/")
def page(path):
    """
    This function handles the majority of Wagtail page requests.

    Renders a Wagtail page by its path, or tries to redirect to an external redirection
    if the page does not exist. If the page is password protected, it redirects to the
    preview page where the user can enter the password.

    If the page has a URL that is different from the requested path, it redirects to
    the canonical URL, which covers internal redirects added in Wagtail and if the
    page is an alias of another page, it redirects to the canonical page.
    """

    try:
        # Get the page details from Wagtail by the requested URI
        page_data = page_details_by_uri(unquote(f"/{path}/"))
    except ResourceNotFound:
        # If no page is found, try to match the requested path with any of the external
        # redirects added in Wagtail
        if current_app.config.get("SERVE_WAGTAIL_EXTERNAL_REDIRECTIONS"):
            return try_external_redirect(path)
        return render_template("errors/page-not-found.html"), 404
    except ResourceForbidden:
        # In the unlikely case that the API returns a 403, show a forbidden error page
        return render_template("errors/forbidden.html"), 403
    except Exception as e:
        # If any other error occurs, log it and return a generic API error page
        # with a 502 status code
        current_app.logger.error(f"Failed to render page: {e}")
        return render_template("errors/api.html"), 502

    # If the page data does not contain meta information, return a 502 error
    # as it is not possible to render the page without it
    if "meta" not in page_data:
        current_app.logger.error("Page meta not available")
        return render_template("errors/api.html"), 502

    # If the page is password protected, redirect to the preview page
    if objects.get(page_data, "meta.privacy") == "password":
        return redirect(
            url_for(
                "wagtail.preview_protected_page",
                page_id=page_data["id"],
            ),
            code=302,
        )

    # We can redirect to an alias page to its canonical page if
    # REDIRECT_WAGTAIL_ALIAS_PAGES is set to True
    if rediect_url := objects.get(page_data, "meta.alias_of.url"):
        if current_app.config.get("REDIRECT_WAGTAIL_ALIAS_PAGES"):
            return redirect(rediect_url, code=302)

    # If the page has a URL that is different from the requested path, redirect to it
    # which covers internal redirects added in Wagtail
    if current_app.config.get("SERVE_WAGTAIL_PAGE_REDIRECTIONS") and (
        urlparse(objects.get(page_data, "meta.url")).path
        != urlparse(f"/{quote(path)}/").path
    ):
        rediect_url = objects.get(page_data, "meta.url")
        return redirect(quote(rediect_url), code=302)

    # Render the page
    return render_content_page(page_data)


def try_external_redirect(path):
    """
    Attempts to fetch and apply a redirect for the given path.

    Returns a redirect response if found, or a 404/502 error page if not found or
    failed.
    """

    # Normalise the path to ensure it starts with a slash and does not end with one
    if not path.startswith("/"):
        path = "/" + path
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]

    # Build a query string from the request arguments
    query_string_keys = request.args.keys()
    query_string = "&".join(
        [f"{key}={request.args.get(key)}" for key in sorted(query_string_keys)]
    )
    if query_string:
        path = f"{path}?{query_string}"

    try:
        # Attempt to get the redirect data by the requested path
        redirect_data = redirect_by_uri(path)
    except ResourceNotFound:
        return render_template("errors/page-not-found.html"), 404
    except Exception as e:
        current_app.logger.error(f"Failed to get redirect: {e}")
        return render_template("errors/api.html"), 502

    # Get the redirect destination and whether it is permanent
    rediect_destination = redirect_data.get("location", "/")
    is_permanent = redirect_data.get("is_permanent", False)

    # Return the redirect to the user
    return redirect(
        rediect_destination,
        code=(301 if is_permanent else 302),
    )


@bp.route("/image/<uuid:image_uuid>/")
def image_page(image_uuid):
    """
    Renders an image details page.
    """

    try:
        image_data = image(image_uuid=image_uuid)
    except ResourceNotFound:
        return render_template("errors/page-not-found.html"), 404
    except ResourceForbidden:
        return render_template("errors/forbidden.html"), 403
    except Exception as e:
        current_app.logger.error(f"Failed to get video: {e}")
        return render_template("errors/api.html"), 502
    return render_template("media/image.html", image_data=image_data)


@bp.route("/search/")
def search():
    """
    Handle search requests and redirect to external search URL.

    URLs are determined by combination of search_type and archive_type:
    - Web + Site: https://webarchive.nationalarchives.gov.uk/ukgwa/timeline1/{site}
    - Web + Keyword: https://webarchive.nationalarchives.gov.uk/search/result?q={query}
    - Social: https://webarchive.nationalarchives.gov.uk/social/search/result?q={query}
    """
    # Get the search query from the request
    query = request.args.get("q", "").strip()
    search_type = request.args.get(
        "search_type", SearchType.KEYWORD.value
    )  # 'keyword' or 'url'
    archive_type = request.args.get(
        "archive_type", ArchiveType.WEB.value
    )  # 'web' or 'social'

    if not query:
        # If no query provided, redirect to the appropriate base search URL
        if archive_type == ArchiveType.SOCIAL.value:
            redirect_url = f"{SOCIAL_SEARCH_BASE}/"
        else:
            redirect_url = f"{WEB_KEYWORD_SEARCH_BASE}/"
        return redirect(redirect_url, code=302)

    # URL encode the query for safe inclusion in URL
    encoded_query = quote_plus(query)

    # Construct external URL based on archive_type and search_type
    if archive_type == ArchiveType.SOCIAL.value:
        # Social archive always uses keyword-style search
        external_url = f"{SOCIAL_SEARCH_BASE}/result?q={encoded_query}"
    elif search_type == SearchType.URL.value:
        # Web + Site search uses timeline1 path
        external_url = f"{WEB_SITE_SEARCH_BASE}/{encoded_query}"
    else:
        # Web + Keyword search
        external_url = f"{WEB_KEYWORD_SEARCH_BASE}/result?q={encoded_query}"

    # Redirect to the external search URL
    return redirect(external_url, code=302)
