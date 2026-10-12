import json
import unittest
from pathlib import Path
from unittest import mock

from coffee_pos.data_access import JSONManager, JSONRepository
from coffee_pos.exceptions import DataFileError, DuplicateError, NotFoundError
from coffee_pos.models import Drink
from tests.helpers import TempDirTestCase


class JSONManagerTests(TempDirTestCase):
    def manager(self, name="data.json"):
        return JSONManager(Path(self.tmp) / name, lambda: [{"seed": 1}])

    def test_missing_file_is_created_with_defaults(self):          # TC-01
        m = self.manager()
        self.assertEqual(m.load(), [{"seed": 1}])
        self.assertTrue(m.path.exists())
        self.assertTrue(any("not found" in e for e in m.events))

    def test_corrupt_json_is_backed_up_and_reset(self):            # TC-02
        m = self.manager()
        m.path.write_text("{ this is not json", encoding="utf-8")
        self.assertEqual(m.load(), [{"seed": 1}])
        backups = list(Path(self.tmp).glob("*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "{ this is not json")

    def test_wrong_json_type_is_recovered(self):
        m = self.manager()
        m.path.write_text('{"a": 1}', encoding="utf-8")
        self.assertEqual(m.load(), [{"seed": 1}])

    def test_empty_file_and_binary_garbage_are_recovered(self):
        for payload in (b"", b"\xff\xfe\x00\x80"):
            with self.subTest(payload=payload):
                m = self.manager()
                m.path.write_bytes(payload)
                self.assertEqual(m.load(), [{"seed": 1}])

    def test_save_is_atomic_and_leaves_no_temp_files(self):
        m = self.manager()
        m.save([{"ชื่อ": "ลาเต้"}])
        self.assertEqual(json.loads(m.path.read_text(encoding="utf-8")),
                         [{"ชื่อ": "ลาเต้"}])
        self.assertEqual(list(Path(self.tmp).glob("*.tmp")), [])

    def test_failed_save_keeps_old_file(self):
        m = self.manager()
        m.save([{"ok": 1}])
        with mock.patch("os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(DataFileError):
                m.save([{"ok": 2}])
        self.assertEqual(json.loads(m.path.read_text()), [{"ok": 1}])
        self.assertEqual(list(Path(self.tmp).glob("*.tmp")), [])

    def test_unserialisable_data_raises_data_file_error(self):
        with self.assertRaises(DataFileError):
            self.manager().save([{"x": object()}])

    def test_unwritable_location_raises_data_file_error(self):
        blocker = Path(self.tmp) / "file"
        blocker.write_text("x")
        m = JSONManager(blocker / "sub" / "data.json")
        with self.assertRaises(DataFileError):
            m.save([])


class RepositoryTests(TempDirTestCase):
    def repo(self, seed=None):
        mgr = JSONManager(Path(self.tmp) / "menu.json",
                          lambda: [d.to_dict() for d in (seed or [])])
        return JSONRepository(mgr, Drink, "drink_id", "Drink")

    def test_crud_persists_across_reload(self):
        r = self.repo()
        r.add(Drink(1, "Latte", 70))
        r.update(Drink(1, "Latte", 75))
        r.add(Drink(2, "Mocha", 80))
        r.delete(2)
        again = self.repo()
        self.assertEqual([(d.drink_id, d.price) for d in again.all()], [(1, 75.0)])

    def test_duplicate_and_missing(self):
        r = self.repo([Drink(1, "Latte", 70)])
        with self.assertRaises(DuplicateError):
            r.add(Drink(1, "Other", 10))
        for call in (lambda: r.get(99), lambda: r.delete(99),
                     lambda: r.update(Drink(99, "x", 1)), lambda: r.get(None),
                     lambda: r.get([1])):
            with self.assertRaises(NotFoundError):
                call()

    def test_invalid_records_are_skipped_and_backed_up(self):
        path = Path(self.tmp) / "menu.json"
        path.write_text(json.dumps([
            {"drink_id": 1, "name": "Latte", "price": 70},
            {"drink_id": 2, "name": "Bad", "price": -5},
            {"drink_id": 3, "name": "NoPrice"},
            "just a string", None, 42,
            {"drink_id": 1, "name": "Dup", "price": 10}]), encoding="utf-8")
        r = self.repo()
        self.assertEqual([d.name for d in r.all()], ["Latte"])
        self.assertTrue(any("skipped 6" in n for n in r.notices))
        self.assertEqual(len(list(Path(self.tmp).glob("*.bak"))), 1)

    def test_memory_rolls_back_when_save_fails(self):
        r = self.repo([Drink(1, "Latte", 70)])
        with mock.patch.object(r._manager, "save", side_effect=DataFileError("boom")):
            with self.assertRaises(DataFileError):
                r.add(Drink(2, "Mocha", 80))
            with self.assertRaises(DataFileError):
                r.update(Drink(1, "Latte", 99))
            with self.assertRaises(DataFileError):
                r.delete(1)
        self.assertEqual([(d.drink_id, d.price) for d in r.all()], [(1, 70.0)])


if __name__ == "__main__":
    unittest.main()
