"""
jobs_writer.py
==============

A lightweight helper for appending job market data to a CSV file.

Purpose
-------
This module defines a `JobRecordDict` TypedDict to represent a single job
record and provides a `write_job_records` function to append multiple records
to a CSV file in bulk.

Features
--------
- Uses Python's built-in `csv` module for safe CSV writing.
- Automatically creates the file and writes the header if it doesn't exist.
- Appends new rows without overwriting existing data.
- Strong typing via `TypedDict` for clarity and static analysis.

Example
-------
    from pathlib import Path
    from jobs_writer import JobRecordDict, write_job_records

    records = [
        JobRecordDict(
            keyword="Node",
            country_region="Romania",
            new_jobs="21",
            date="Jul 21, 2025, 2:55 PM"
        ),
        JobRecordDict(
            keyword="Python",
            country_region="Bangladesh",
            new_jobs="15",
            date="Sep 13, 2025, 10:30 AM"
        ),
    ]

    write_job_records(records, Path("jobs.csv"))
"""

import csv
from pathlib import Path
from typing import List, TypedDict


class JobRecordDict(TypedDict):
    """
    Represents a single job record for CSV storage.

    Attributes:
        keyword: Name of the keyword (e.g., "Node", "Python").
        country_region: Country or region name.
        new_jobs: Number of new jobs.
        date: Date/time string in the desired display format.
    """

    keyword: str
    country_region: str
    new_jobs: str
    date: str


def write_job_records(records: List[JobRecordDict], csv_path: Path) -> None:
    """
    Append job records to a CSV file. Creates the file with a header if it doesn't exist.

    Args:
        records: List of JobRecordDict entries to write.
        csv_path: Path to the CSV file.

    Notes:
        - The header row is written only if the file is new.
        - Data is appended; existing rows are preserved.
    """
    if not records:
        return  # Nothing to write

    file_exists = csv_path.exists()

    # Open file in append mode, ensuring newline='' to avoid blank lines on Windows
    with csv_path.open(mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header if file is new
        if not file_exists:
            writer.writerow(["Keyword", "Country/Region", "New Jobs", "Date"])

        # Write each record as a row
        for record in records:
            writer.writerow(
                [
                    record["keyword"],
                    record["country_region"],
                    record["new_jobs"],
                    record["date"],
                ]
            )
