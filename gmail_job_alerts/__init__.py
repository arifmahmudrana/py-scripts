"""
Gmail Job Alerts Automation Package
===================================

This package automates the processing of LinkedIn job alert emails received
in Gmail. It provides tools to:

- Authenticate with Gmail using OAuth2.
- Fetch unread LinkedIn job alert messages.
- Extract structured job information (keywords, regions, job counts, dates).
- Collect and persist LinkedIn job URLs.
- Mark messages as read and move them into a predefined Gmail label.
- Write structured job records to CSV for further analysis.

Modules
-------
- auth:
    Authentication utilities for Gmail API (OAuth2).
- utils:
    Helper functions for decoding, parsing, and configuration management.
- processor:
    Core logic for fetching and processing LinkedIn job alerts.
- jobs_writer:
    Functions for writing job records to CSV.
- urls_db:
    SQLite-backed persistence for LinkedIn job URLs.

Public API
----------
By default, only the following database functions are exposed at the
package level:

- `read_urls(limit: int = 5) -> Generator[str, None, None]`
  Yield up to `limit` stored LinkedIn job URLs for downstream processing.

- `delete_urls(*urls: str) -> None`
  Delete one or more URLs from the database after they have been processed.

Example
-------
Typical usage of the exposed database functions:

```python
from gmail_job_alerts import read_urls, delete_urls

# Read up to 10 stored job URLs
for url in read_urls(limit=10):
    print("Processing:", url)
    # ... do something with the URL ...
    delete_urls(url)  # remove after processing
```

Notes
-----
- Internal helpers such as `_init_db`, `_log_failures`, and `write_batch`
  remain private and are not imported into the package namespace.
- This keeps the public API minimal and focused on the most common tasks.
"""

from .urls_db import read_urls, delete_urls

# Define the public API of the package
__all__ = ["read_urls", "delete_urls"]
