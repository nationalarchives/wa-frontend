from app.api import bp
from app.lib import archive_service
from flask import current_app, jsonify, request


@bp.route("/archive/characters", methods=["GET"])
def archive_characters():
    """
    Get list of characters that have archive records.

    Returns:
        JSON response with format:
        {
            "characters": ["0-9", "a", "b", ...],
            "count": 27
        }
    """
    try:
        characters = archive_service.get_available_characters()
        return (
            jsonify(
                {
                    "characters": characters,
                    "count": len(characters),
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching available characters: {e}")
        return (
            jsonify(
                {
                    "error": "Failed to fetch available characters",
                    "message": str(e) if current_app.debug else "Internal server error",
                }
            ),
            500,
        )


@bp.route("/archive/records", methods=["GET"])
def archive_records():
    """
    Get archive records filtered by character.

    Query parameters:
        character (required): First character to filter by (e.g., 'a', '0-9')

    Returns:
        JSON response with format:
        {
            "items": [
                {
                    "id": 1,
                    "profile_name": "Example Site",
                    "record_url": "https://example.com",
                    "archive_link": "https://webarchive...",
                    "domain_type": "Central government",
                    "first_capture_display": "2010",
                    "latest_capture_display": "2024",
                    "ongoing": true,
                    "wam_id": 12345,
                    "description": "...",
                    "sort_name": "example site",
                    "first_character": "e"
                }
            ],
            "meta": {
                "total_count": 100,
            }
        }
    """
    character = request.args.get("character", "").strip().lower()

    if not character:
        return (
            jsonify(
                {
                    "error": "Missing required parameter",
                    "message": "Parameter 'character' is required",
                }
            ),
            400,
        )

    try:
        result = archive_service.get_records_by_character(character=character)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(
            f"Error fetching records for character '{character}': {e}"
        )
        return (
            jsonify(
                {
                    "error": "Failed to fetch archive records",
                    "message": str(e) if current_app.debug else "Internal server error",
                }
            ),
            500,
        )


@bp.route("/archive/stats", methods=["GET"])
def archive_stats():
    """
    Get archive statistics.

    Returns:
        JSON response with format:
        {
            "total_records": 1234,
            "characters_count": 27
        }

    Status codes:
        200: Success
        500: Internal server error
    """
    try:
        total_records = archive_service.get_record_count()
        characters = archive_service.get_available_characters()

        return (
            jsonify(
                {
                    "total_records": total_records,
                    "characters_count": len(characters),
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Error fetching archive stats: {e}")
        return (
            jsonify(
                {
                    "error": "Failed to fetch archive statistics",
                    "message": str(e) if current_app.debug else "Internal server error",
                }
            ),
            500,
        )


@bp.route("/health", methods=["GET"])
def api_health():
    """
    Simple health check endpoint for the API.

    Returns:
        JSON response with status
    """
    return jsonify({"status": "ok"}), 200
