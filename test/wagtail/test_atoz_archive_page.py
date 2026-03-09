import unittest
from unittest.mock import patch

from app.lib.archive_service import _sanitize_fts_query
from app.wagtail.pages.atoz_archive_page import render_atoz_archive_page

from app import create_app

PAGE_DATA = {
    "id": 1,
    "title": "A to Z Archive",
    "intro": "",
    "meta": {
        "url": "/archive/atoz/",
        "type": "ukgwa.AToZArchivePage",
    },
}

AVAILABLE_CHARACTERS = ["0-9", "a", "b", "c", "d", "g", "z"]

SEARCH_RESULTS = {
    "items": [
        {
            "id": 1,
            "profile_name": "Government Digital Service",
            "record_url": "https://gds.example.com",
            "archive_link": "https://webarchive.example.com/gds",
            "domain_type": "Central government",
            "first_capture_display": "2012",
            "latest_capture_display": "2024",
            "ongoing": False,
            "wam_id": 42,
            "description": "The Government Digital Service.",
            "sort_name": "government digital service",
            "first_character": "g",
        }
    ],
    "meta": {"total_count": 1},
}

CHARACTER_RESULTS = {
    "items": [
        {
            "id": 2,
            "profile_name": "Department for Digital",
            "record_url": "https://dfd.example.com",
            "archive_link": "https://webarchive.example.com/dfd",
            "domain_type": "Central government",
            "first_capture_display": "2015",
            "latest_capture_display": "2023",
            "ongoing": False,
            "wam_id": 99,
            "description": "Department for Digital.",
            "sort_name": "department for digital",
            "first_character": "d",
        }
    ],
    "meta": {"total_count": 1},
}


class AtozArchivePageSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test")
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def _render(self, query_string=""):
        with (
            patch(
                "app.lib.archive_service.get_available_characters",
                return_value=AVAILABLE_CHARACTERS,
            ),
            patch(
                "app.lib.archive_service.search_records",
                return_value=SEARCH_RESULTS,
            ),
            patch(
                "app.lib.archive_service.get_records_by_character",
                return_value=CHARACTER_RESULTS,
            ),
        ):
            with self.app.test_request_context(f"/?{query_string}"):
                result = render_atoz_archive_page(PAGE_DATA)
        # Normalise: success returns a Response; errors return (string, status)
        if isinstance(result, tuple):
            return result
        return result.get_data(as_text=True), result.status_code

    def test_empty_q_renders_index(self):
        """?q= with no character returns index page."""
        response, status = self._render("q=")
        self.assertEqual(status, 200)
        self.assertIn("Browse by character", response)

    def test_empty_q_with_character_renders_listing(self):
        """?character=d&q= ignores empty search and returns character listing."""
        response, status = self._render("character=d&q=")
        self.assertEqual(status, 200)
        self.assertIn("Department for Digital", response)

    def test_search_overrides_character(self):
        """?character=a&q=foo calls search_records, ignoring the character param."""
        with (
            patch(
                "app.lib.archive_service.get_available_characters",
                return_value=AVAILABLE_CHARACTERS,
            ) as _mock_chars,  # noqa F841
            patch(
                "app.lib.archive_service.search_records",
                return_value=SEARCH_RESULTS,
            ) as mock_search,
            patch(
                "app.lib.archive_service.get_records_by_character",
            ) as mock_by_char,
        ):
            with self.app.test_request_context("/?character=a&q=foo"):
                render_atoz_archive_page(PAGE_DATA)

        mock_search.assert_called_once_with("foo")
        mock_by_char.assert_not_called()

    def test_basic_search_returns_results(self):
        """?q=government displays matching records."""
        response, status = self._render("q=government")
        self.assertEqual(status, 200)
        self.assertIn("Government Digital Service", response)
        self.assertIn('Search results for "government"', response)

    def _render_response(self, query_string=""):
        """Returns the raw Response object for header inspection."""
        with (
            patch(
                "app.lib.archive_service.get_available_characters",
                return_value=AVAILABLE_CHARACTERS,
            ),
            patch(
                "app.lib.archive_service.search_records",
                return_value=SEARCH_RESULTS,
            ),
            patch(
                "app.lib.archive_service.get_records_by_character",
                return_value=CHARACTER_RESULTS,
            ),
        ):
            with self.app.test_request_context(f"/?{query_string}"):
                return render_atoz_archive_page(PAGE_DATA)

    def test_search_results_have_noindex_header(self):
        """Search results response includes X-Robots-Tag: noindex."""
        result = self._render_response("q=government")
        self.assertEqual(result.headers.get("X-Robots-Tag"), "noindex")

    def test_character_page_has_no_noindex_header(self):
        """Character listing does not include X-Robots-Tag: noindex."""
        result = self._render_response("character=d")
        self.assertIsNone(result.headers.get("X-Robots-Tag"))

    def test_index_page_has_no_noindex_header(self):
        """Index page does not include X-Robots-Tag: noindex."""
        result = self._render_response()
        self.assertIsNone(result.headers.get("X-Robots-Tag"))

    def test_character_not_in_available_returns_404(self):
        """?character=x where x is not in available_characters returns 404."""
        response, status = self._render("character=x")
        self.assertEqual(status, 404)

    def test_all_available_characters_return_200(self):
        """Every character in available_characters returns a 200 listing."""
        for char in AVAILABLE_CHARACTERS:
            with self.subTest(char=char):
                response, status = self._render(f"character={char}")
                self.assertEqual(status, 200)

    def test_available_character_with_no_records_returns_500(self):
        """A character in available_characters that returns no records is a data error."""
        with (
            patch(
                "app.lib.archive_service.get_available_characters",
                return_value=AVAILABLE_CHARACTERS,
            ),
            patch(
                "app.lib.archive_service.get_records_by_character",
                return_value={"items": []},
            ),
        ):
            with self.app.test_request_context("/?character=a"):
                _, status = render_atoz_archive_page(PAGE_DATA)
        self.assertEqual(status, 500)


class SanitizeFtsQueryTestCase(unittest.TestCase):
    def test_plain_query_is_unchanged(self):
        self.assertEqual(_sanitize_fts_query("government"), "government")

    def test_hash_is_stripped(self):
        self.assertEqual(_sanitize_fts_query("#10 Downing"), "10 Downing")

    def test_at_sign_is_stripped(self):
        self.assertEqual(_sanitize_fts_query("site@example"), "site example")

    def test_fts5_wildcard_preserved(self):
        self.assertEqual(_sanitize_fts_query("digit*"), "digit*")

    def test_fts5_phrase_preserved(self):
        self.assertEqual(
            _sanitize_fts_query('"government digital"'), '"government digital"'
        )

    def test_fts5_boolean_operators_preserved(self):
        self.assertEqual(
            _sanitize_fts_query("health AND digital"), "health AND digital"
        )
        self.assertEqual(_sanitize_fts_query("health OR digital"), "health OR digital")
        self.assertEqual(
            _sanitize_fts_query("health NOT digital"), "health NOT digital"
        )

    def test_leading_boolean_operator_stripped(self):
        self.assertEqual(_sanitize_fts_query("AND government"), "government")
        self.assertEqual(_sanitize_fts_query("OR government"), "government")
        self.assertEqual(_sanitize_fts_query("NOT government"), "government")

    def test_trailing_boolean_operator_stripped(self):
        self.assertEqual(_sanitize_fts_query("government AND"), "government")
        self.assertEqual(_sanitize_fts_query("government OR"), "government")

    def test_leading_wildcard_stripped(self):
        self.assertEqual(_sanitize_fts_query("*government"), "government")

    def test_unmatched_quote_stripped(self):
        self.assertEqual(_sanitize_fts_query('"government'), "government")

    def test_unbalanced_parentheses_stripped(self):
        self.assertEqual(_sanitize_fts_query("(health OR digital"), "health OR digital")

    def test_empty_string_returns_empty(self):
        self.assertEqual(_sanitize_fts_query(""), "")

    def test_query_truncated_to_max_length(self):
        from app.lib.util import ARCHIVE_SEARCH_MAX_LENGTH

        long_query = "a" * (ARCHIVE_SEARCH_MAX_LENGTH + 50)
        result = _sanitize_fts_query(long_query)
        self.assertLessEqual(len(result), ARCHIVE_SEARCH_MAX_LENGTH)
