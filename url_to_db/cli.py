"""Command line interface for url_to_db."""

import argparse
from .core import process_urls_to_db


def run_from_args(argv=None):
    """Parse command line arguments and run the URL to DB processor."""
    parser = argparse.ArgumentParser(
        description="Extract URLs from text file and write to database."
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to YAML config file with keys: input_text_file, domain_filter, unique_only",
    )

    args = parser.parse_args(argv)

    # Process URLs and write to database
    count = process_urls_to_db(args.config)
    print(f"Successfully processed {count} URLs to database.")
