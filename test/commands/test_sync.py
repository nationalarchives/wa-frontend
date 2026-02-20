import unittest
from unittest.mock import MagicMock, patch

from app.commands import (
    _clear_cache,
    delete_entries,
    save_entries,
    save_entry,
    validate_entries,
)
from app.lib import archive_service, database
from app.lib.cache import cache
from app.lib.models import ArchiveRecord

from app import create_app

VALID_ENTRY = {
    "profileName": "Example Site",
    "entryUrl": "https://example.com",
    "archiveLink": "https://webarchive.nationalarchives.gov.uk/example",
    "domainType": "Central government",
    "firstCapture": "2010-01-01",
    "firstCaptureDisplay": "2010",
    "latestCapture": "2024-01-01",
    "latestCaptureDisplay": "2024",
    "ongoing": True,
    "wamId": 1,
    "wamLink": "https://wam.example.com/1",
    "parentId": None,
    "generatedOn": "2024-01-01",
    "currentDepartments": [],
    "previousDepartments": [],
    "description": "An example site",
}


def _make_validated(wam_id=1, profile_name="Example Site"):
    from app.lib.schemas import ArchiveRecordSchema

    return ArchiveRecordSchema(
        **{**VALID_ENTRY, "wamId": wam_id, "profileName": profile_name}
    )


def _num_db_records():
    return database.db_session.query(ArchiveRecord).count()


class ValidateEntriesTestCase(unittest.TestCase):
    def test_empty_input(self):
        validated, errors = validate_entries([])
        self.assertEqual(len(validated), 0)
        self.assertEqual(errors, 0)

    def test_valid_entry_is_accepted(self):
        validated, errors = validate_entries([VALID_ENTRY])
        self.assertEqual(len(validated), 1)
        self.assertEqual(errors, 0)

    def test_invalid_entry_is_counted(self):
        invalid = {**VALID_ENTRY, "entryUrl": "not-a-url"}
        validated, errors = validate_entries([invalid])
        self.assertEqual(len(validated), 0)
        self.assertEqual(errors, 1)

    def test_mixed_entries(self):
        invalid = {**VALID_ENTRY, "wamId": -1}
        validated, errors = validate_entries([invalid, VALID_ENTRY])
        self.assertEqual(len(validated), 1)
        self.assertEqual(errors, 1)


class SaveEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        database.Base.metadata.create_all(database.engine)

    def tearDown(self):
        database.db_session.remove()
        database.Base.metadata.drop_all(database.engine)
        self.app_context.pop()

    def test_creates_new_record(self):
        validated = _make_validated()
        self.assertEqual(_num_db_records(), 0)

        result = save_entry(validated, {})
        self.assertEqual(_num_db_records(), 1)
        self.assertEqual(result, "created")

    def test_skips_unchanged_record(self):
        """
        The existing record is mocked to simulate an unchanged record (matching hash).
        """
        validated = _make_validated()
        existing = MagicMock(spec=ArchiveRecord)
        existing.record_hash = validated.record_hash
        result = save_entry(validated, {1: existing})
        self.assertEqual(result, "skipped")

    def test_updates_changed_record(self):
        """
        The existing record is mocked with a different hash to simulate a record that
        has changed since the last sync.
        """
        validated = _make_validated()
        existing = MagicMock(spec=ArchiveRecord)
        existing.record_hash = "different_hash"
        result = save_entry(validated, {1: existing})
        self.assertEqual(result, "updated")


class DeleteEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        database.Base.metadata.create_all(database.engine)

    def tearDown(self):
        database.db_session.remove()
        database.Base.metadata.drop_all(database.engine)
        self.app_context.pop()

    def _add_record(self, wam_id):
        validated = _make_validated(wam_id)
        data = validated.model_dump(mode="json", by_alias=False, exclude={"wam_id"})
        record = ArchiveRecord(wam_id=wam_id, **data)
        database.db_session.add(record)
        database.db_session.commit()

    def test_deletes_records_not_in_source(self):
        self._add_record(1)
        self._add_record(2)
        self.assertEqual(_num_db_records(), 2)

        query = database.db_session.query(ArchiveRecord).filter(
            ArchiveRecord.wam_id.not_in([1])
        )
        count = delete_entries(query, dry_run=False)
        self.assertEqual(count, 1)
        self.assertEqual(_num_db_records(), 1)

    def test_dry_run_does_not_delete(self):
        self._add_record(1)
        self._add_record(2)
        self.assertEqual(_num_db_records(), 2)

        query = database.db_session.query(ArchiveRecord).filter(
            ArchiveRecord.wam_id.not_in([1])
        )
        count = delete_entries(query, dry_run=True)
        self.assertEqual(count, 1)
        self.assertEqual(_num_db_records(), 2)


class ClearCacheTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test")
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("app.commands.cache")
    @patch("app.commands.get_records_by_character")
    def test_clears_cache_on_live_run(self, mock_get_records, mock_cache):
        _clear_cache(dry_run=False)
        mock_cache.delete.assert_called_once_with("archive:characters")
        mock_cache.delete_memoized.assert_called_once_with(mock_get_records)

    @patch("app.commands.cache")
    def test_skips_cache_clear_on_dry_run(self, mock_cache):
        _clear_cache(dry_run=True)
        mock_cache.delete.assert_not_called()
        mock_cache.delete_memoized.assert_not_called()


class CacheInvalidationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.Test")
        self.app_context = self.app.app_context()
        self.app_context.push()
        database.Base.metadata.create_all(database.engine)
        cache.clear()

    def tearDown(self):
        database.db_session.remove()
        database.Base.metadata.drop_all(database.engine)
        self.app_context.pop()

    def _save(self, validated):
        save_entries([validated], 1, 1000, dry_run=False)

    def test_cache_is_stale_without_invalidation(self):
        """Without clearing the cache, updated data is not reflected."""
        validated = _make_validated(1, profile_name="Earlier Site")
        self._save(validated)

        # Prime the cache
        result_before = archive_service.get_records_by_character("e")
        self.assertEqual(result_before["items"][0]["profile_name"], "Earlier Site")

        # Update the record without clearing cache
        updated = _make_validated(1, profile_name="Enhanced Site")
        self._save(updated)

        # Cache still returns old result
        result_after = archive_service.get_records_by_character("e")
        self.assertEqual(result_after["items"][0]["profile_name"], "Earlier Site")

    def test_cache_is_fresh_after_invalidation(self):
        """After clearing the cache, updated data is reflected."""
        validated = _make_validated(1, profile_name="Earlier Site")
        self._save(validated)

        # Prime the cache
        archive_service.get_records_by_character("e")

        # Update the record and clear cache
        updated = _make_validated(1, profile_name="Enhanced Site")
        self._save(updated)
        _clear_cache(dry_run=False)

        # Cache now returns new result
        result_after = archive_service.get_records_by_character("e")
        self.assertEqual(result_after["items"][0]["profile_name"], "Enhanced Site")
