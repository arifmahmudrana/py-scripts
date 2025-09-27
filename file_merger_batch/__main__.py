"""
__main__.py

CLI entrypoint for batch file merger.
"""

import argparse
import sys
from .batch_merger import merge_files_in_batches


def main():
    parser = argparse.ArgumentParser(
        description="Batch file merger using glob patterns and YAML config."
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Path to YAML config file."
    )
    args = parser.parse_args()

    merge_files_in_batches(args.config)


if __name__ == "__main__":
    sys.exit(main())
