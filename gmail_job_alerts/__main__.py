"""
Gmail Job Alerts Automation – Entry Point
=========================================

This script serves as the command‑line entry point for automating the
processing of LinkedIn job alert emails retrieved from Gmail.

Overview
--------
The script reads a configuration file (YAML or JSON) that specifies:
    - **csv_file_path**: Path to the CSV file where extracted job records
      will be written.
    - **email_timezone**: Time zone string used to interpret email dates.
    - **accounts**: A mapping of account identifiers (e.g., "personal",
      "work") to Gmail label names where LinkedIn job alerts are stored.
    - **keywords**: A list of technology or skill keywords to match against
      job alert subjects.
    - **countries_or_regions**: A list of location keywords to filter jobs.

For each configured account/label pair, the script invokes
`process_linkedin_jobs`, which handles:
    - Fetching unread job alert messages from Gmail.
    - Parsing email details and filtering by keywords/regions.
    - Writing structured job records to the configured CSV file.

Usage
-----
Run the script as a module, passing the path to your configuration file:

    python -m gmail_job_alerts --config gmail_job_alerts/config.yaml

Example configuration file (YAML):
----------------------------------
```yaml
csv_file_path: "jobs.csv"
email_timezone: "UTC"
accounts:
  personal: "LinkedInJobs"
keywords:
  - python
  - data engineer
countries_or_regions:
  - Germany
  - Bangladesh
```

Error Handling
--------------
- Raises `FileNotFoundError` if the config file does not exist.
- Raises `ValueError` if required keys are missing or no accounts are defined.

Notes
-----
- The Gmail API will authenticate while running this script.
- Labels referenced in the config must already exist in the Gmail account.
"""

import argparse
from typing import Dict, List

from .processor import process_linkedin_jobs
from .utils import load_config


def main() -> None:
    """
    Command‑line entry point for automating LinkedIn job alert processing.

    Steps performed:
        1. Parse the `--config` argument to locate the YAML/JSON config file.
        2. Load configuration values (CSV path, timezone, accounts, filters).
        3. Validate that required fields are present.
        4. Iterate over each account/label pair and process job alerts.

    Raises:
        FileNotFoundError: If the config file path does not exist.
        ValueError: If required keys are missing or no accounts are defined.
    """
    parser = argparse.ArgumentParser(
        description="Automate LinkedIn job alert processing from Gmail."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to config file (YAML or JSON). Example: accounts.yaml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    csv_file_path: str = config.get("csv_file_path", "")
    if not csv_file_path:
        raise ValueError("No csv_file_path found in config file.")
    email_timezone: str = config.get("email_timezone", "")
    if not email_timezone:
        raise ValueError("No email_timezone found in config file.")
    accounts: Dict[str, str] = config.get("accounts", {})
    keywords: List[str] = config.get("keywords", [])
    countries_or_regions: List[str] = config.get("countries_or_regions", [])

    if not accounts:
        raise ValueError("No accounts found in config file.")

    for account, label in accounts.items():
        print(
            f"\n=== Processing LinkedIn Jobs ===\nAccount: {account}\nLabel  : {label}\n"
        )
        process_linkedin_jobs(
            account,
            label,
            csv_file_path,
            email_timezone,
            keywords,
            countries_or_regions,
        )


if __name__ == "__main__":
    main()
