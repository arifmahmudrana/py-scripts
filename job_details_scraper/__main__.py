"""
job_details_scraper.__main__
============================

Entry point for running the `job_details_scraper` package as a module via:

    python -m job_details_scraper

This script starts the job URL processing loop.

Environment Variables
---------------------
Although this script does not consume environment variables directly,
other components (such as database access and logging configuration)
depend on the following being set before running:

- GJA_DB_PATH : Path to the SQLite database file (`urls.db`) that contains
  pending job URLs to be processed.
- GJA_LOG_PATH : Path to the log file where logs will be written.

Example Usage
-------------
Run the scraper with required environment variables set:

    GJA_DB_PATH=./urls.db GJA_LOG_PATH=./logs/scraper.log \
        python -m job_details_scraper

Execution Flow
--------------
1. Call `process_all_job_urls` with fixed directories for saving raw HTML
   and parsed text data.
2. Continue processing until no URLs remain or a termination signal
   (SIGINT/SIGTERM) is received.
"""

import sys
from pathlib import Path

from .job_url_processor import process_all_job_urls


def main() -> None:
    """Main entry point for the job details scraper."""
    print("[INFO] Starting job_details_scraper")

    # Base directory of this file (job_details_scraper package)
    base_dir = Path(__file__).resolve().parent

    # Fixed directories for saving outputs, relative to package dir
    html_dir = base_dir / "html"
    txt_dir = base_dir / "text"

    try:
        process_all_job_urls(html_dir=html_dir, txt_dir=txt_dir, batch_size=5)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"[ERROR] Fatal error while processing job URLs: {exc}")
        sys.exit(1)

    print("[INFO] job_details_scraper finished successfully.")


if __name__ == "__main__":
    main()
