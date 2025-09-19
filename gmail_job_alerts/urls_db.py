"""
urls_db.py
==========

A lightweight, memory‑friendly SQLite helper for managing a queue of URLs.

This module is designed for scenarios such as web crawlers, scrapers, or
batch processors where URLs need to be stored, retrieved in small batches,
and removed once processed — keeping the database size minimal.

Key Features:
-------------
- **Single-column schema**: Only stores the URL as a PRIMARY KEY.
- **Batch insert**: `write_batch(urls)` inserts multiple URLs at once,
  ignoring duplicates automatically.
- **Streaming read**: `read_urls(limit)` yields up to `limit` URLs one by one,
  allowing immediate processing without loading all results into memory.
- **Delete on process**: `delete_urls(*urls)` removes processed URLs entirely
  from the database to keep file size small.
- **Retry logging**: Any failed DB operations are logged to `db_failures.log`
  for later retry.

Performance & Safety:
---------------------
- Uses SQLite PRAGMA settings for safe concurrent reads/writes (`WAL` mode)
  and maximum durability (`synchronous=FULL`).
- Generator expressions are used for inserts and deletes to avoid building
  large intermediate lists in memory.

Intended Usage:
---------------
This module is meant to be imported into your application code. The functions
are prefixed with an underscore to indicate they are internal helpers by
convention, not part of a public API.

Example:
--------
    import urls_db

    # Add URLs
    urls_db.write_batch([
        "https://example.com/1",
        "https://example.com/2"
    ])

    # Read and process
    for url in urls_db.read_urls(limit=5):
        print("Processing:", url)
        # ... do work ...
        urls_db.delete_urls(url)

    # Failed operations can be inspected in 'db_failures.log'
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Generator
import os

DB_PATH = Path(os.getenv("GJA_DB_PATH", "./gmail_job_alerts/urls.db"))
LOG_PATH = Path(os.getenv("GJA_LOG_PATH", "./gmail_job_alerts/db_failures.log"))

# Configure logging for retries
logging.basicConfig(
    filename=LOG_PATH, level=logging.ERROR, format="%(asctime)s - %(message)s"
)


def _init_db() -> sqlite3.Connection:
    """Initialize the database and return a connection."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = FULL;")
    cur.execute("PRAGMA temp_store = MEMORY;")
    cur.execute("PRAGMA cache_size = -64000;")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            url TEXT PRIMARY KEY
        )
    """
    )
    conn.commit()
    return conn


def _log_failures(action: str, urls: List[str], error: Exception):
    """Log failed URLs for retry."""
    for u in urls:
        logging.error("%s failed for %s | Error: %s", action, u, error)


def write_batch(urls: List[str]) -> None:
    """Insert URLs in batch, ignoring duplicates."""
    if not urls:
        return
    conn = _init_db()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO urls (url) VALUES (?)", ((u,) for u in urls)
        )
        conn.commit()
    except sqlite3.Error as e:
        _log_failures("INSERT", urls, e)
    finally:
        conn.close()


def read_urls(limit: int = 5) -> Generator[str, None, None]:
    """Yield up to `limit` URLs one by one."""
    conn = _init_db()
    try:
        cur = conn.execute("SELECT url FROM urls LIMIT ?", (limit,))
        for row in cur:
            yield row[0]
    finally:
        conn.close()


def delete_urls(*urls: str) -> None:
    """Delete given URLs from the database."""
    if not urls or len(urls) == 0:
        return
    conn = _init_db()
    try:
        conn.executemany("DELETE FROM urls WHERE url = ?", ((u,) for u in urls))
        conn.commit()
    except sqlite3.Error as e:
        _log_failures("DELETE", list(urls), e)
    finally:
        conn.close()
