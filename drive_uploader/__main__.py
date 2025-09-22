"""
CLI entrypoint for drive_uploader.

Usage:
    python -m drive_uploader --config config.yaml
"""

import argparse
from .auth import get_service
from .drive_ops import ensure_path
from .uploader import upload_files
from .utils import load_config


def main():
    parser = argparse.ArgumentParser(description="Upload local files to Google Drive.")
    parser.add_argument("--config", required=True, help="Path to YAML config file.")
    args = parser.parse_args()

    config = load_config(args.config)
    service = get_service(
        config.get("credentials_file_path"), config.get("token_file_path")
    )

    jobs = config.get("jobs", [])
    if not jobs:
        print("No jobs defined in config.")
        return

    for job in jobs:
        target_path = job["target_path"]
        local_pattern = job["local_pattern"]
        print(
            f"\n=== Processing job ===\nTarget: {target_path}\nPattern: {local_pattern}"
        )
        folder_id = ensure_path(service, target_path)
        upload_files(service, folder_id, local_pattern)


if __name__ == "__main__":
    main()
