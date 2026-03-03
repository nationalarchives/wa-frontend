from app.lib import archive_service
from app.lib.util import (
    ARCHIVE_SEARCH_MAX_LENGTH,
    DIGITS_CATEGORY,
    normalize_archive_letter,
)
from flask import current_app, render_template, request


def render_atoz_archive_page(page_data):
    """
    Handler for A-to-Z Archive Page.

    Renders either:
    - Index view: Grid of available characters with links
    - Listing view: Filtered archive records for a specific character

    Query parameter:
    - character: Character to filter by (a-z, or '0-9' for digits and special chars)
    """
    character = normalize_archive_letter(request.args.get("character", ""))
    search_query = request.args.get("q", "").strip()

    # Fetch available characters from local database
    try:
        available_characters = archive_service.get_available_characters()
    except Exception as e:
        current_app.logger.error(f"Failed to get available characters: {e}")
        return render_template("errors/server.html"), 500

    if not character and not search_query:
        return render_template(
            "pages/atoz/index.html",
            page_data=page_data,
            available_characters=available_characters,
            search_max_length=ARCHIVE_SEARCH_MAX_LENGTH,
        )

    try:
        if search_query:
            result = archive_service.search_records(search_query)
        else:
            if character not in available_characters:
                current_app.logger.warning(
                    f"Invalid character parameter '{character}' for A-to-Z archive"
                )
                return render_template("errors/page-not-found.html"), 404

            result = archive_service.get_records_by_character(character)
    except Exception as e:
        current_app.logger.error(
            f"Failed to get archive records on page {page_data['id']}: {e}"
        )
        return render_template("errors/server.html"), 500

    records = result.get("items", [])
    display_character = (
        character
        if character == DIGITS_CATEGORY
        else character.upper() if character else None
    )

    return render_template(
        "pages/atoz/listing.html",
        page_data=page_data,
        records=records,
        selected_character=character,
        display_character=display_character,
        available_characters=available_characters,
        search_query=search_query,
        search_max_length=ARCHIVE_SEARCH_MAX_LENGTH,
    )
