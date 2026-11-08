import os
import sqlite3
import tempfile
import unittest

from konsumo.database import init_db, connect
from konsumo.repository import add_record, list_records, get_record, update_record, delete_record
from konsumo.web.auth import AuthError, authenticate, create_user


class MultiAccountTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.temp.name, "test.sqlite3")
        init_db(self.db)
        self.alice = create_user("Alice", "alice@example.com", "password123", self.db)
        self.bob = create_user("Bob", "bob@example.com", "password456", self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_signup_and_login_support_multiple_accounts(self):
        self.assertEqual(authenticate("ALICE@example.com", "password123", self.db)["id"], self.alice["id"])
        self.assertEqual(authenticate("bob@example.com", "password456", self.db)["id"], self.bob["id"])

    def test_duplicate_email_is_rejected(self):
        with self.assertRaises(AuthError):
            create_user("Other", "ALICE@example.com", "password789", self.db)

    def test_records_are_isolated_by_account(self):
        alice_record = add_record("electricity", "2026-11-01", 12, db_path=self.db, user_id=self.alice["id"])
        add_record("water", "2026-11-02", 4, db_path=self.db, user_id=self.bob["id"])

        self.assertEqual([r["id"] for r in list_records(db_path=self.db, user_id=self.alice["id"])], [alice_record])
        self.assertEqual(len(list_records(db_path=self.db, user_id=self.bob["id"])), 1)
        self.assertIsNone(get_record(alice_record, db_path=self.db, user_id=self.bob["id"]))

    def test_users_cannot_edit_or_delete_another_users_record(self):
        record_id = add_record("electricity", "2026-11-01", 10, db_path=self.db, user_id=self.alice["id"])
        with self.assertRaises(ValueError):
            update_record(record_id, db_path=self.db, user_id=self.bob["id"],
                          resource="electricity", recorded_at="2026-11-02", amount=20)
        with self.assertRaises(ValueError):
            delete_record(record_id, db_path=self.db, user_id=self.bob["id"])
        self.assertIsNotNone(get_record(record_id, db_path=self.db, user_id=self.alice["id"]))

    def test_legacy_records_are_assigned_to_first_account(self):
        legacy_db = os.path.join(self.temp.name, "legacy.sqlite3")
        with sqlite3.connect(legacy_db) as conn:
            conn.execute("""CREATE TABLE consumption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                amount REAL NOT NULL,
                cost REAL,
                notes TEXT NOT NULL DEFAULT ''
            )""")
            conn.execute("INSERT INTO consumption(resource,recorded_at,amount) VALUES ('water','2026-01-01',3)")
        init_db(legacy_db)
        user = create_user("Legacy owner", "legacy@example.com", "password123", legacy_db)
        rows = list_records(db_path=legacy_db, user_id=user["id"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], 3)


if __name__ == "__main__":
    unittest.main()
