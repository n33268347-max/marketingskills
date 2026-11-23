"""SQLite access layer. All research tables are append-only (enforced by triggers)."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Any, Iterator, Mapping

log = logging.getLogger(__name__)

SCHEMA_VERSION = "1"


class ImmutableRecordError(RuntimeError):
    """Raised when code tries to modify an append-only record."""


def connect(path: str | Path) -> sqlite3.Connection:
    """Open (and initialise if needed) a research database."""
    path = str(path)
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_schema(conn)
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    sql = resources.files("raffle_edge.db").joinpath("schema.sql").read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.execute(
        "INSERT OR IGNORE INTO schema_meta(key, value) VALUES ('schema_version', ?)",
        (SCHEMA_VERSION,),
    )
    conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    try:
        yield conn
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if "append-only" in str(exc):
            raise ImmutableRecordError(str(exc)) from exc
        raise
    except Exception:
        conn.rollback()
        raise


def insert(conn: sqlite3.Connection, table: str, row: Mapping[str, Any]) -> int:
    """Insert one row and return its rowid. Table/column names come from code, never user input."""
    if not table.isidentifier():
        raise ValueError(f"bad table name {table!r}")
    cols = [c for c in row if row[c] is not None]
    for c in cols:
        if not c.isidentifier():
            raise ValueError(f"bad column name {c!r}")
    placeholders = ", ".join("?" for _ in cols)
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    cur = conn.execute(sql, [row[c] for c in cols])
    return int(cur.lastrowid)


def ensure_platform(conn: sqlite3.Connection, slug: str, name: str, base_url: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO platforms(slug, name, base_url) VALUES (?, ?, ?)",
        (slug, name, base_url),
    )


def ensure_competition(conn: sqlite3.Connection, platform_slug: str, external_ref: str, name: str) -> int:
    row = conn.execute(
        "SELECT id FROM competitions WHERE platform_slug = ? AND external_ref = ?",
        (platform_slug, external_ref),
    ).fetchone()
    if row:
        return int(row["id"])
    return insert(conn, "competitions", {"platform_slug": platform_slug, "external_ref": external_ref, "name": name})
