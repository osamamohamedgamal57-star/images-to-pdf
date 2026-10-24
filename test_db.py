import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import db

NOW = datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.mkdtemp()
        db.DB_PATH = os.path.join(folder, "test.db")
        db.init_db()

    def test_same_user_is_counted_once(self):
        db.track_user(1, "ali", "Ali", now=NOW)
        db.track_user(1, "ali", "Ali", now=NOW + timedelta(hours=1))
        stats = db.get_stats(NOW)
        self.assertEqual(stats["total_users"], 1)
        self.assertEqual(stats["new_today"], 1)
        self.assertEqual(stats["active_today"], 1)

    def test_new_active_returning_and_regular_users(self):
        # user 1 joined 20 days ago and came back yesterday and today
        for days_back in (20, 1, 0):
            db.track_user(1, "old", "Old", now=NOW - timedelta(days=days_back))
        # user 2 joined today
        db.track_user(2, "new", "New", now=NOW)
        stats = db.get_stats(NOW)
        self.assertEqual(stats["total_users"], 2)
        self.assertEqual(stats["new_today"], 1)
        self.assertEqual(stats["new_7d"], 1)
        self.assertEqual(stats["new_30d"], 2)
        self.assertEqual(stats["active_today"], 2)
        self.assertEqual(stats["active_7d"], 2)
        self.assertEqual(stats["returning_7d"], 1)
        self.assertEqual(stats["regular_30d"], 1)

    def test_inactive_user_is_not_active(self):
        db.track_user(1, "gone", "Gone", now=NOW - timedelta(days=40))
        stats = db.get_stats(NOW)
        self.assertEqual(stats["total_users"], 1)
        self.assertEqual(stats["active_30d"], 0)
        self.assertEqual(stats["returning_7d"], 0)

    def test_pdf_counts(self):
        db.record_pdf(1, 3, now=NOW)
        db.record_pdf(1, 2, now=NOW - timedelta(days=3))
        stats = db.get_stats(NOW)
        self.assertEqual(stats["pdfs_total"], 2)
        self.assertEqual(stats["pdfs_today"], 1)

    def test_settings(self):
        self.assertEqual(db.get_setting("max_images"), "30")
        db.set_setting("max_images", "10")
        self.assertEqual(db.get_setting("max_images"), "10")

    def test_admins(self):
        self.assertFalse(db.is_admin(5))
        db.add_admin(5)
        self.assertTrue(db.is_admin(5))
        db.remove_admin(5)
        self.assertFalse(db.is_admin(5))


if __name__ == "__main__":
    unittest.main()
