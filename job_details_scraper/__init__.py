"""
Job Details Scraper Package
============================

This package is primarily designed to scrape job details from job
detail URLs. It is most often run as a command‑line utility, similar
to how one might use `venv` or other CLI tools. In addition to the
CLI entry point, the package also provides a small set of utility
functions that can be imported and reused in other programs if needed.

Public API
----------
Currently, the main exposed utility is:

- `exponential_backoff_retry`: a decorator that adds retry logic with
  exponential backoff. While useful for wrapping network or scraping
  functions that may fail transiently, it is still experimental and
  not yet thoroughly tested. It is configurable in terms of:
    * maximum number of retries
    * base delay and maximum delay
    * which exceptions should trigger a retry

Example
-------
```python
from retry_utils import exponential_backoff_retry

@exponential_backoff_retry(
    max_retries=3, base_delay=2.0, exceptions_to_retry=(ConnectionError,))
def fetch_data():
    # Simulate a flaky operation
    ...
```

In this example, `fetch_data` will be retried up to 3 times if it raises
a `ConnectionError`, with delays of 2s, 4s, and 8s (plus random jitter).

Notes
-----
- Only `exponential_backoff_retry` is exported at the package level.
- Internal helpers, examples, or test code remain private.
"""

from .retry_utils import exponential_backoff_retry

__all__ = ["exponential_backoff_retry"]
