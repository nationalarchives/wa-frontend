from enum import StrEnum

from app.lib import archive_service
from app.lib.util import (
    ARCHIVE_SEARCH_MAX_LENGTH,
    DIGITS_CATEGORY,
    normalize_archive_letter,
)
from flask import current_app, make_response, render_template, request


class DisplayMode(StrEnum):
    INDEX = "index"
    LISTING = "listing"
    SEARCH = "search"


def render_atoz_archive_page(page_data):
    """
    Handler for A-to-Z Archive Page.

    Renders one of three states depending on query parameters:
    - Index view: character browse list, no records shown
    - Listing view: archive records filtered by a specific character
    - Search view: archive records matching a full-text search query

    Query parameters:
    - character: Character to filter by (a-z, or '0-9' for digits)
    - q: Full-text search query (takes precedence over character)

    Search results responses include X-Robots-Tag: noindex.
    """
    character = normalize_archive_letter(request.args.get("character", ""))
    search_query = request.args.get("q", "").strip()

    try:
        available_characters = archive_service.get_available_characters()
    except Exception as e:
        current_app.logger.error(f"Failed to get available characters: {e}")
        return render_template("errors/server.html"), 500

    records = None
    display_mode = (
        DisplayMode.SEARCH
        if search_query
        else DisplayMode.LISTING if character else DisplayMode.INDEX
    )

    if search_query:
        try:
            result = archive_service.search_records(search_query)
            records = result.get("items", [])
        except Exception as e:
            current_app.logger.error(
                f"Failed to get archive records on page {page_data['id']}: {e}"
            )
            return render_template("errors/server.html"), 500
    elif character:
        if character not in available_characters:
            current_app.logger.warning(
                f"Invalid character parameter '{character}' for A-to-Z archive"
            )
            return render_template("errors/page-not-found.html"), 404
        try:
            result = archive_service.get_records_by_character(character)
            records = result.get("items", [])
        except Exception as e:
            current_app.logger.error(
                f"Failed to get archive records on page {page_data['id']}: {e}"
            )
            return render_template("errors/server.html"), 500

    display_character = (
        character
        if character == DIGITS_CATEGORY
        else character.upper() if character else None
    )

    response = make_response(
        render_template(
            "pages/atoz_page.html",
            page_data=page_data,
            records=records,
            selected_character=character,
            display_character=display_character,
            available_characters=available_characters,
            search_query=search_query,
            search_max_length=ARCHIVE_SEARCH_MAX_LENGTH,
            display_mode=display_mode,
        )
    )

    if search_query:
        response.headers["X-Robots-Tag"] = "noindex"

    return response
