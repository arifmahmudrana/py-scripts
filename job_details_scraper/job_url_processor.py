"""
job_url_processor.py
====================

Module for safely processing LinkedIn job URLs stored in the local SQLite
database (`urls.db`). This script continuously reads URLs in batches,
fetches job details for each using the `get_job_details_from_url` function,
and deletes them once processed.

Features
--------
- Reads job URLs from the database in configurable batch sizes.
- Calls a user-supplied job details fetcher with retry logic.
- Deletes URLs after successful processing.
- Handles termination signals (SIGINT, SIGTERM) gracefully to avoid leaks.
- Ensures database connections and generators are properly closed.

Usage
-----
Typical usage from another script:

```python
from pathlib import Path
from .job_url_processor import process_all_job_urls

process_all_job_urls(
    html_dir=Path("./html"),
    txt_dir=Path("./txt"),
    batch_size=10,
)
```

This will:
1. Continuously fetch up to 10 URLs at a time from the database.
2. For each URL, extract the job ID and call `get_job_details_from_url`.
3. Delete processed URLs from the database.
4. Exit cleanly when the database is empty or the user presses Ctrl+C.
"""

import signal
from pathlib import Path
from types import FrameType
from typing import Any, Dict, List, Optional

from gmail_job_alerts import read_urls, delete_urls
from .linkedin_scraper import (
    get_job_details_from_url,
)  # adjust import to your actual module

# Global flag to indicate termination requested
_stop_requested = False


def _handle_exit(signum: int, _frame: Optional[FrameType]) -> None:
    """
    Signal handler to request graceful shutdown.

    Sets a global flag that is checked between batches and per-URL processing.
    """
    global _stop_requested
    _stop_requested = True
    print(f"\n[INFO] Received signal {signum}, shutting down gracefully...")


# Register signal handlers for Ctrl+C (SIGINT) and SIGTERM
signal.signal(signal.SIGINT, _handle_exit)
signal.signal(signal.SIGTERM, _handle_exit)


def process_all_job_urls(
    html_dir: Optional[Path] = None,
    txt_dir: Optional[Path] = None,
    batch_size: int = 5,
) -> None:
    """
    Continuously read job URLs from the database, fetch job details for each,
    and delete them once processed. Stops when DB is empty or termination
    signal is received.

    Args:
        html_dir (Optional[Path]):
            Directory to save raw HTML responses (if supported by fetcher).
        txt_dir (Optional[Path]):
            Directory to save parsed text (if supported by fetcher).
        batch_size (int):
            Number of URLs to fetch per batch (default: 5).
    """
    global _stop_requested

    while not _stop_requested:
        # Fully consume the generator into a list to ensure closure
        urls: List[str] = list(read_urls(limit=batch_size))
        if not urls:
            print("[INFO] No more URLs in database.")
            break

        for url in urls:
            if _stop_requested:
                break
            # LinkedIn job URLs are normalized like .../jobs/view/<job_id>/
            job_id = url.rstrip("/").split("/")[-1]
            print(f"[INFO] Fetching details for job '{job_id}' from '{url}'...")
            details: Dict[str, Any] = get_job_details_from_url(
                url, job_id, html_dir=html_dir, txt_dir=txt_dir
            )
            print(f"[INFO] Processed job {job_id}: {details}")
            for key, value in details.items():
                print(f"    - {key}: {value}")

        # Delete processed URLs
        try:
            delete_urls(*urls)
        except Exception as e:
            print(f"[ERROR] Failed to delete URLs {urls}: {e}")

    print("[INFO] Job details processing loop exited.")
