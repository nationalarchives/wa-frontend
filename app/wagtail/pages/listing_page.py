import math

from flask import current_app, render_template, request
from tna_utilities.url import QueryStringTransformer

from app.lib.pagination import pagination
from app.wagtail.api import page_children_paginated


def render_listing_page(page_data):
    children_per_page = current_app.config.get("PAGINATION_PAGE_SIZE", 12)
    page = 1
    if request.args.get("page"):
        try:
            page = int(request.args.get("page", 1))
        except ValueError:
            return render_template("errors/bad_request.html"), 400
    if page < 1:
        return render_template("errors/bad_request.html"), 400
    try:
        children_data = page_children_paginated(
            page_data["id"],
            page,
            children_per_page,
        )
    except ConnectionError:
        current_app.logger.error(
            f"API error getting children for page {page_data['id']}"
        )
        return render_template("errors/api.html"), 502
    except Exception:  # noqa: BLE001
        current_app.logger.error(
            f"Exception getting children for page {page_data['id']}"
        )
        return render_template("errors/server.html"), 500
    pages = math.ceil(children_data["meta"]["total_count"] / children_per_page)
    if page > pages > 0:
        return render_template("errors/page_not_found.html"), 404

    qs = QueryStringTransformer(list(request.args.lists()), tolerant=True)

    return render_template(
        "pages/listing.html",
        page_data=page_data,
        children=children_data["items"],
        pagination=pagination(qs, pages, page),
        page=page,
        pages=pages,
    )
