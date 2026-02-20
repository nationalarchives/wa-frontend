from app.lib import archive_service
from flask import current_app, render_template, request


def render_atoz_page(page_data):
    return render_template(
        "pages/atoz_page.html",
        page_data=page_data,
    )


def render_atoz_archive_page(page_data):
    """
    Handler for A-to-Z Archive Page.

    Renders either:
    - Index view: Grid of available characters with links
    - Listing view: Filtered archive records for a specific character

    Query parameter:
    - character: Character to filter by (a-z, or '0-9' for digits and special chars)
    """
    character = request.args.get("character", "").strip()
    # Normalize alphabetic characters to lowercase, keep '0-9' as-is
    if character and character.isalpha():
        character = character.lower()

    # Fetch available characters from local database
    try:
        available_characters = archive_service.get_available_characters()
    except Exception as e:
        current_app.logger.error(f"Failed to get available characters: {e}")
        return render_template("errors/internal_server_error.html"), 500

    if not character:
        return render_template(
            "pages/atoz/index.html",
            page_data=page_data,
            available_characters=available_characters,
        )

    if character not in available_characters:
        current_app.logger.warning(
            f"Invalid character parameter '{character}' for A-to-Z archive"
        )
        return render_template("errors/page_not_found.html"), 404

    try:
        result = archive_service.get_records_by_character(character)
        records = result.get("items", [])
    except Exception as e:
        current_app.logger.error(
            f"Failed to get archive records for character '{character}' on page {page_data['id']}: {e}"
        )
        return render_template("errors/internal_server_error.html"), 500

    display_character = character if character == "0-9" else character.upper()

    return render_template(
        "pages/atoz/listing.html",
        page_data=page_data,
        records=records,
        selected_character=character,
        display_character=display_character,
        available_characters=available_characters,
    )
