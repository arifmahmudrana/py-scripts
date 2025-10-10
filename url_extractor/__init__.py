"""
url_extractor

Lightweight package to extract URLs from a text file, filter by domain,
and write (optionally unique) output to a file.

Intended to be used both as a module and as a CLI via `python -m url_extractor`.
"""

__version__ = "0.1.0"

from .core import (
    load_yaml_config,
    extract_urls_from_text,
    filter_urls_by_domain,
    write_urls_to_file,
)

__all__ = [
    "load_yaml_config",
    "extract_urls_from_text",
    "filter_urls_by_domain",
    "write_urls_to_file",
]
