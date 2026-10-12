"""SQLite connection and schema setup for the POS data store."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3

from coffee_pos.exceptions import DatabaseError


def load_project_env() -> None:
    """Load simple KEY=VALUE settings from the repository's untracked .env."""
    root = Path(__file__).resolve().parents[2]
    env_file = root / ".env"
    if not env_file.exists():
        return
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DatabaseError(f"Cannot read .env: {exc}") from exc
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if name and name not in os.environ:
            os.environ[name] = value


class SQLiteDatabase:
    """Creates the SQLite file/schema and opens short-lived connections."""

    def __init__(self, path=None):
        load_project_env()
        configured_path = path or os.getenv("SQLITE_DATABASE")
        self.path = Path(configured_path) if configured_path else (
            Path(__file__).resolve().parents[2] / "data" / "coffee_pos.sqlite3"
        )
        if not self.path.is_absolute():
            self.path = Path(__file__).resolve().parents[2] / self.path
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._ensure_schema()
        except (OSError, sqlite3.Error) as exc:
            raise DatabaseError(f"Cannot initialize SQLite database at {self.path}: {exc}") from exc

    def connect(self):
        try:
            connection = sqlite3.connect(self.path, timeout=10)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except sqlite3.Error as exc:
            raise DatabaseError(f"Cannot connect to SQLite database at {self.path}: {exc}") from exc

    @contextmanager
    def session(self):
        """Commit or roll back a short transaction, then always close it."""
        connection = self.connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _ensure_schema(self):
        statements = (
            """CREATE TABLE IF NOT EXISTS drinks (
                drink_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                price REAL NOT NULL CHECK (price >= 0)
            )""",
            """CREATE TABLE IF NOT EXISTS members (
                phone TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                discount_rate REAL NOT NULL DEFAULT 0.1
            )""",
            """CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                total REAL NOT NULL CHECK (total >= 0),
                payload TEXT NOT NULL
            )""",
        )
        with self.session() as connection:
            for statement in statements:
                connection.execute(statement)
