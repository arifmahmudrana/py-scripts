"""
Core utilities for URL extraction and filtering.

Functions:
- load_yaml_config(path)
- extract_urls_from_text(text)
- filter_urls_by_domain(urls, domain_filter)
- get_unique_urls(urls)
- write_urls_to_file(urls, dest_path, unique=True)
"""

from typing import Iterable, List, Set
import re
from pathlib import Path
import yaml

# Simple regex to capture typical URLs (http/https)
URL_REGEX = re.compile(
    r"""(?xi)
    \b
    (?:
      https?://
    )
    [^\s<>"'()]+
    """
)


def load_yaml_config(path: str) -> dict:
    """Load YAML configuration from `path` and return as dict."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    # Basic validation and defaults
    required = ["input_text_file", "output_file", "domain_filter", "unique_only"]
    for r in required:
        if r not in data:
            raise KeyError(f"Missing required config key: {r}")
    return data


def extract_urls_from_text(text: str) -> List[str]:
    """Return all URL strings found in `text` using a conservative regex."""
    return URL_REGEX.findall(text)


def extract_urls_from_file(path: str) -> List[str]:
    """Read file and extract URLs."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input text file not found: {path}")
    text = p.read_text(encoding="utf-8")
    return extract_urls_from_text(text)


def filter_urls_by_domain(urls: Iterable[str], domain_filter: str) -> List[str]:
    """
    Filter URLs that contain the domain_filter string (case-insensitive).
    e.g. domain_filter = "www.udemy.com" or "udemy.com"
    """
    df_lower = domain_filter.lower()
    return [u for u in urls if df_lower in u.lower()]


def get_unique_urls(urls: Iterable[str]) -> List[str]:
    """
    Return unique URLs preserving original order.

    Args:
        urls: Iterable of URL strings

    Returns:
        List of unique URLs in original order

    Example:
        >>> urls = ["https://a.com", "https://b.com", "https://a.com"]
        >>> get_unique_urls(urls)
        ['https://a.com', 'https://b.com']
    """
    seen: Set[str] = set()
    unique_urls: List[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    return unique_urls


def write_urls_to_file(
    urls: Iterable[str], dest_path: str, unique: bool = True
) -> None:
    """
    Write URLs to dest_path, one per line. If unique=True, keep original order and
    drop duplicates.
    """
    p = Path(dest_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if unique:
        final_list = get_unique_urls(urls)
    else:
        final_list = list(urls)

    # Write with newline at the end of each URL
    p.write_text("\n".join(final_list) + ("\n" if final_list else ""), encoding="utf-8")
