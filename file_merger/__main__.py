"""
__main__.py

Entry point for CLI usage of file_merger.
"""

import argparse
import sys
from .merger import merge_files_with_formatting, load_config


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple files with configurable prefix, join, suffix, and final append."
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to YAML config file (first_prepend, prefix, join, suffix, final_append, output_path).",
    )
    parser.add_argument("files", nargs="+", help="List of input files to merge.")

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Merge files
    merge_files_with_formatting(
        *args.files,
        first_prepend=config.get("first_prepend", ""),
        prefix=config.get("prefix", ""),
        join=config.get("join", "\n"),
        suffix=config.get("suffix", ""),
        final_append=config.get("final_append", ""),
        output_path=config.get("output_path", "output.txt")
    )


if __name__ == "__main__":
    sys.exit(main())
