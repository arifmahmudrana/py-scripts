"""
Core functionality for extracting URLs and writing to database.

This module combines url_extractor functionality with gmail_job_alerts database
operations to provide a simple pipeline: text file → URL extraction → database.

Functions:
- load_yaml_config(path): Load YAML configuration
- strip_url_query_params(url): Remove query parameters from URL
- process_urls_to_db(config_path): Main processing function
"""

from typing import List
from pathlib import Path
from urllib.parse import urlparse, urlunparse
import yaml

# Import from url_extractor
from url_extractor.core import (
    extract_urls_from_file,
    filter_urls_by_domain,
)

# Import from gmail_job_alerts
from gmail_job_alerts.urls_db import write_batch


def load_yaml_config(path: str) -> dict:
    """
    Load YAML configuration from path and return as dict.

    Args:
        path: Path to YAML config file

    Returns:
        Dictionary containing config values

    Raises:
        FileNotFoundError: If config file doesn't exist
        KeyError: If required config keys are missing
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    # Validate required keys
    required = ["input_text_file", "domain_filter", "unique_only"]
    for r in required:
        if r not in data:
            raise KeyError(f"Missing required config key: {r}")

    return data


def strip_url_query_params(url: str) -> str:
    """
    Remove query parameters from URL.

    Args:
        url: URL string (e.g., "https://example.com/page?foo=bar&baz=qux")

    Returns:
        URL without query parameters (e.g., "https://example.com/page")

    Example:
        >>> strip_url_query_params("https://example.com/page?foo=bar")
        'https://example.com/page'
    """
    parsed = urlparse(url)
    # Reconstruct URL without query and fragment
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def process_urls_to_db(config_path: str) -> int:
    """
    Extract URLs from text file and write to database.

    This function:
    1. Loads configuration from YAML file
    2. Extracts URLs from the input text file
    3. Filters URLs by domain
    4. Optionally strips query parameters from URLs
    5. Optionally removes duplicates (keeping original order)
    6. Writes URLs to the SQLite database

    Args:
        config_path: Path to YAML configuration file

    Returns:
        Number of URLs processed and written to database

    Example:
        >>> count = process_urls_to_db("config.yaml")
        >>> print(f"Processed {count} URLs")
    """
    # Load configuration
    cfg = load_yaml_config(config_path)

    # Extract URLs from file
    urls = extract_urls_from_file(cfg["input_text_file"])
    print(f"Extracted {len(urls)} URLs from file")

    # Filter by domain
    urls = filter_urls_by_domain(urls, cfg["domain_filter"])
    print(f"Filtered to {len(urls)} URLs matching domain: {cfg['domain_filter']}")

    # Strip query parameters if requested
    if cfg.get("strip_query_params", False):
        urls = [strip_url_query_params(u) for u in urls]
        print(f"Stripped query parameters from URLs")

    # Remove duplicates if requested (preserve order)
    if cfg["unique_only"]:
        seen = set()
        unique_urls: List[str] = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)
        urls = unique_urls
        print(f"Kept {len(urls)} unique URLs")

    # Write to database
    write_batch(urls)
    print(f"Wrote {len(urls)} URLs to database")

    return len(urls)
