"""
Utility Functions for Gmail Job Alerts
======================================

This module provides helper utilities for parsing Gmail messages, extracting
job information, and loading configuration files for the Gmail Job Alerts
automation workflow.

Overview
--------
The functions in this module support the following tasks:

- **Configuration Management**
  - `Config` (TypedDict): Defines the expected structure of the YAML/JSON
    configuration file.
  - `load_config`: Loads and validates configuration from disk.

- **Message Decoding and Parsing**
  - `decode_base64url`: Decodes Gmail's base64url‑encoded message bodies.
  - `extract_msg_date`: Extracts and formats the `Date` header from Gmail
    messages, with optional timezone conversion.

- **Job Alert Extraction**
  - `match_subject_keyword`: Finds relevant keywords in email subjects.
  - `extract_job_count`: Determines the number of jobs mentioned in a subject
    or body.
  - `extract_region`: Identifies the geographic region mentioned in a job alert.
  - `extract_job_urls`: Extracts and normalizes LinkedIn job URLs from email
    content.

Dependencies
------------
- Standard library: `base64`, `email.utils`, `json`, `re`, `pathlib.Path`,
  `typing`, `zoneinfo`.
- Optional: `PyYAML` (for YAML config support). If not installed, only JSON
  configs are supported.

Configuration File Structure
----------------------------
The configuration file defines how job alerts are processed. It must be in
YAML or JSON format and follow the `Config` schema:

```yaml
csv_file_path: "jobs.csv"
email_timezone: "UTC"
accounts:
  personal: "LinkedInJobs"
keywords:
  - python
countries_or_regions:
  - Germany
```

Functions
---------
- `decode_base64url(data: str) -> str`
  Decodes Gmail's base64url‑encoded message bodies into UTF‑8 strings.

- `load_config(path: str) -> Config`
  Loads configuration from a `.yaml`, `.yml`, or `.json` file. Raises
  `FileNotFoundError` if the file is missing, `ImportError` if YAML is
  requested but PyYAML is not installed, and `ValueError` for unsupported
  formats.

- `match_subject_keyword(subject: str, keywords: List[str]) -> Optional[str]`
  Returns the first keyword found in the subject (case‑insensitive), or `None`.

- `extract_job_count(subject: str, body: str) -> Optional[str]`
  Extracts job counts from subject/body text. Handles patterns like
  `"30+ new jobs"`, `"12 new jobs"`, or `"A new job"`. Returns a string
  representation of the count (e.g., `"30+"`, `"12"`, `"1"`), or `None`.

- `extract_region(body: str, regions: List[str]) -> Optional[str]`
  Returns the first matching region from the provided list, or `None`.

- `extract_job_urls(body: str) -> List[str]`
  Finds LinkedIn job URLs in the body, normalizes them to the canonical
  `https://www.linkedin.com/jobs/view/<job_id>/` format, and deduplicates
  them while preserving order.

- `extract_msg_date(msg: Dict[str, Any], tz: Optional[str] = None) -> Optional[str]`
  Extracts the `Date` header from a Gmail API message resource and formats it
  as `"Sep 9, 2025, 3:10 AM"`. If `tz` is provided, converts to that timezone.

Error Handling
--------------
- `load_config` raises:
  - `FileNotFoundError` if the config file does not exist.
  - `ImportError` if YAML parsing is requested but PyYAML is not installed.
  - `ValueError` if the file extension is unsupported.
- Extraction functions return `None` if no match is found.

Notes
-----
- All keyword and region matching is case‑insensitive.
- `extract_job_urls` strips query parameters and normalizes URLs.
- `extract_msg_date` ensures day and hour values are not zero‑padded for
  readability (e.g., `"3:05 AM"` instead of `"03:05 AM"`).
"""

import base64
import email.utils
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict
from zoneinfo import ZoneInfo

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


class Config(TypedDict):
    """
    Represents the structure of the application's configuration file.

    Keys:
        csv_file_path (str):
            A CSV file path where the analysis would be written.

        email_timezone (str):
            Timezone which you want to convert of your email e.g. "UTC".

        accounts (Dict[str, str]):
            A mapping of account identifiers to their corresponding names or handles.
            Keys are arbitrary strings (e.g., "personal", "work", "test_account"),
            and values are the associated account names.

        keywords (List[str]):
            A list of Keywords to be tracked or processed.

        countries_or_regions (List[str]):
            A list of country or region names relevant to the application's scope.
    """

    csv_file_path: str
    email_timezone: str
    accounts: Dict[str, str]
    keywords: List[str]
    countries_or_regions: List[str]


def decode_base64url(data: str) -> str:
    """
    Decode a base64url-encoded Gmail message body.

    Args:
        data: Base64url encoded string.

    Returns:
        Decoded string.
    """
    return base64.urlsafe_b64decode(data).decode("utf-8")


def load_config(path: str) -> Config:
    """
    Load configuration from a YAML or JSON file.

    Args:
        path: Path to config file.

    Returns:
        Parsed config as dictionary.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    text = config_path.read_text(encoding="utf-8")

    if path.endswith((".yaml", ".yml")):
        if not yaml:
            raise ImportError(
                "PyYAML is required for YAML config support."
                " Install with `pip install pyyaml`."
            )
        return yaml.safe_load(text)
    elif path.endswith(".json"):
        return json.loads(text)

    raise ValueError("""Unsupported config file format. Use .yaml, .yml, or .json""")


def match_subject_keyword(subject: str, keywords: List[str]) -> Optional[str]:
    """
    Find the first keyword that appears in the email subject.

    The subject is lowercased before comparison, and keywords are assumed to be
    case-insensitive matches.

    Args:
        subject: The email subject string.
        keywords: A list of keywords to search for.

    Returns:
        The first keyword found in the subject (as provided in the list),
        or None if no match is found.

    Example:
        >>> match_subject_keyword("30+ new jobs for 'nodejs'", ["golang", "nodejs"])
        'nodejs'
        >>> match_subject_keyword("Senior Engineer Role", ["golang", "python"])
        None
    """
    subject_lower = subject.lower()

    for keyword in keywords:
        if keyword.lower() in subject_lower:
            return keyword  # return the matched keyword from the list

    return None


def extract_job_count(subject: str, body: str) -> Optional[str]:
    """
    Attempt to extract the number of jobs mentioned in an email's subject or body.

    Extraction logic:
      1. Search the subject line for patterns like:
         - "30+ new jobs for 'nodejs'"
         - "12 new jobs for 'python'"
         - "1 new job for 'golang'"
         The numeric portion is captured (e.g., "30", "12", "1").
      2. If no match is found in the subject, search the body text with the same pattern.
      3. If still no match, but the body contains the phrase "A new job"
         (case-insensitive), assume a count of 1.
      4. If no condition matches, return None.

    Return value:
        - A string representation of the job count.
        - Special case: if the count is exactly 30, return "30+".
        - Otherwise, return the number as a string (e.g., "12", "1").
        - Returns None if no count can be determined.

    Args:
        subject: The email subject string.
        body: The email body string.

    Returns:
        str | None: The extracted job count as a string, or None if not found.

    Examples:
        >>> extract_job_count("30+ new jobs for 'nodejs'", "")
        "30+"
        >>> extract_job_count("12 new jobs for 'python'", "")
        "12"
        >>> extract_job_count("Random subject", "A new job matches your preferences")
        "1"
        >>> extract_job_count("Irrelevant subject", "Some other text")
        None
    """
    regex = r"(\d+)\s*\+?\s*new job[s]?"
    match = re.search(regex, subject.lower())
    if not match:
        match = re.search(regex, body.lower())
    job_counts = (
        int(match.group(1)) if match else 1 if "A new job" in body.lower() else None
    )

    return (
        None
        if job_counts is None
        else f"{job_counts}+" if job_counts == 30 else f"{job_counts}"
    )


def extract_region(body: str, regions: List[str]) -> Optional[str]:
    """
    Extract the region from an email body by matching against a list of regions.

    The search is case-insensitive. The function returns the first region from
    the list that is found in the body text.

    Args:
        body: The plain-text email body.
        regions: A list of regions to search for (e.g., ["Australia", "Sweden", "New Zealand"]).

    Returns:
        The matched region (string) if found, otherwise None.

    Example:
        >>> body = "Your job alert for nodejs in Australia and New Zealand"
        >>> extract_region(body, ["Australia", "Sweden", "New Zealand"])
        'Australia'

        >>> extract_region(body, ["India", "Germany"])
        None
    """
    body_lower = body.lower()

    for region in regions:
        if region.lower() in body_lower:
            return region  # return the matched region as provided

    return None


def extract_job_urls(body: str) -> List[str]:
    """
    Extract and normalize all unique LinkedIn job URLs from an email body.

    This function searches both plain text and HTML content for job links that
    match the LinkedIn job view pattern. It removes query parameters and ensures
    URLs are normalized into the canonical format:
        https://www.linkedin.com/jobs/view/<job_id>/

    Deduplication is applied while preserving the original order of appearance.

    Args:
        body: The plain-text or HTML email body.

    Returns:
        A list of unique normalized job URLs. The list may be empty if no URLs are found.

    Example:
        >>> body = "View job: https://www.linkedin.com/comm/jobs/view/4296631213/?trackingId=abc123"
        >>> extract_job_urls(body)
        ['https://www.linkedin.com/jobs/view/4296631213/']
    """
    # Regex: match job URLs with or without /comm/ and capture job ID
    pattern = re.compile(
        r"https://www\.linkedin\.com/(?:comm/)?jobs/view/(\d+)", re.IGNORECASE
    )

    matches = pattern.findall(body)
    normalized_urls = [
        f"https://www.linkedin.com/jobs/view/{job_id}/" for job_id in matches
    ]

    # Deduplicate while keeping order
    unique_urls = list(dict.fromkeys(normalized_urls))

    return unique_urls


def extract_msg_date(
    msg: Dict[str, Any],
    tz: Optional[str] = None,
) -> Optional[str]:
    """
    Extract the Date header from a Gmail API message and return a nicely
    formatted string like: "Sep 9, 2025, 3:10 AM".

    Args:
        msg: A Gmail API message resource (dictionary).
        tz: Optional timezone string (e.g., "UTC", "Asia/Dhaka").
            If None, keep the datetime in its original timezone.

    Returns:
        A string with the formatted datetime, or None if parsing fails.
    """
    headers = msg.get("payload", {}).get("headers", [])
    date_str = next((h["value"] for h in headers if h.get("name") == "Date"), None)
    if not date_str:
        return None

    # Parse RFC 2822 date
    dt = email.utils.parsedate_to_datetime(date_str)
    if not dt:
        return None

    # Convert timezone if specified
    if tz:
        dt = dt.astimezone(ZoneInfo(tz))

    # Build the string in parts (day without zero padding)
    month = dt.strftime("%b")  # "Sep"
    day = str(dt.day)  # "9" (no zero padding)
    year = dt.strftime("%Y")  # "2025"

    # But `%I` is always zero-padded → fix by casting int
    hour = str(int(dt.strftime("%I")))  # ensures "3" not "03"
    minute = dt.strftime("%M")
    ampm = dt.strftime("%p")

    return f"{month} {day}, {year}, {hour}:{minute} {ampm}"
