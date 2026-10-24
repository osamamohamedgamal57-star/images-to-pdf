"""Small SQLite database: users, daily activity, created PDFs, settings and admins.
All times are stored in UTC."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

# The database always lives next to this file, so it does not matter where the bot is started from
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.db")

DEFAULT_SETTINGS = {
    "welcome_text": (
        "Hi! I turn your images into one PDF.\n\n"
        "1. Send me your photos (one by one or as an album)\n"
        "2. Type /pdf and I will send you the file\n"
        "3. Type /clear if you want to start over"
    ),
    "max_images": "30",
}


@contextmanager
def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now():
    return datetime.now(timezone.utc)


def _day(now, days_back):
    return (now.date() - timedelta(days=days_back)).isoformat()


def init_db():
    with _db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS activity (
                user_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                PRIMARY KEY (user_id, day)
            );
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                pages INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY
            );
            """
        )
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))


# ---------- users and activity ----------
def track_user(user_id, username, first_name, now=None):
    """Save a new user, or update an existing one. Also marks the user as active today."""
    now = now or _now()
    stamp = now.isoformat(timespec="seconds")
    with _db() as conn:
        conn.execute(
            """INSERT INTO users (user_id, username, first_name, first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(user_id) DO UPDATE SET
                   username = excluded.username,
                   first_name = excluded.first_name,
                   last_seen = excluded.last_seen""",
            (user_id, username, first_name, stamp, stamp),
        )
        conn.execute(
            "INSERT OR IGNORE INTO activity (user_id, day) VALUES (?, ?)",
            (user_id, now.date().isoformat()),
        )


def record_pdf(user_id, pages, now=None):
    now = now or _now()
    with _db() as conn:
        conn.execute(
            "INSERT INTO pdfs (user_id, created_at, pages) VALUES (?, ?, ?)",
            (user_id, now.isoformat(timespec="seconds"), pages),
        )


def get_stats(now=None):
    now = now or _now()
    today, week_start, month_start = _day(now, 0), _day(now, 6), _day(now, 29)
    with _db() as conn:

        def one(sql, *args):
            return conn.execute(sql, args).fetchone()[0]

        return {
            "total_users": one("SELECT COUNT(*) FROM users"),
            "new_today": one("SELECT COUNT(*) FROM users WHERE first_seen >= ?", today),
            "new_7d": one("SELECT COUNT(*) FROM users WHERE first_seen >= ?", week_start),
            "new_30d": one("SELECT COUNT(*) FROM users WHERE first_seen >= ?", month_start),
            "active_today": one("SELECT COUNT(DISTINCT user_id) FROM activity WHERE day >= ?", today),
            "active_7d": one("SELECT COUNT(DISTINCT user_id) FROM activity WHERE day >= ?", week_start),
            "active_30d": one("SELECT COUNT(DISTINCT user_id) FROM activity WHERE day >= ?", month_start),
            # joined before this week AND used the bot in the last 7 days
            "returning_7d": one(
                """SELECT COUNT(*) FROM users u
                   WHERE u.first_seen < ?
                   AND EXISTS (SELECT 1 FROM activity a WHERE a.user_id = u.user_id AND a.day >= ?)""",
                week_start,
                week_start,
            ),
            # used the bot on 3 or more different days in the last 30 days
            "regular_30d": one(
                """SELECT COUNT(*) FROM (
                       SELECT user_id FROM activity WHERE day >= ?
                       GROUP BY user_id HAVING COUNT(*) >= 3)""",
                month_start,
            ),
            "pdfs_total": one("SELECT COUNT(*) FROM pdfs"),
            "pdfs_today": one("SELECT COUNT(*) FROM pdfs WHERE created_at >= ?", today),
        }


# ---------- settings ----------
def get_setting(key):
    with _db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else DEFAULT_SETTINGS[key]


def set_setting(key, value):
    with _db() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )


# ---------- admins ----------
def is_admin(user_id):
    with _db() as conn:
        return conn.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,)).fetchone() is not None


def add_admin(user_id):
    with _db() as conn:
        conn.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))


def remove_admin(user_id):
    with _db() as conn:
        conn.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))


def list_admins():
    with _db() as conn:
        return [row["user_id"] for row in conn.execute("SELECT user_id FROM admins ORDER BY user_id")]
