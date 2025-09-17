"""
Processor for Gmail Job Alerts
==============================

This module contains the core logic for processing unread LinkedIn job alert
emails from Gmail. It authenticates with the Gmail API, fetches unread job
alert messages, extracts relevant job information (keywords, regions, job
counts, job URLs, and dates), and writes the results to persistent storage.

Workflow
--------
1. Authenticate with Gmail using OAuth2 credentials.
2. Query unread messages from LinkedIn job alert senders.
3. For each message:
   - Extract subject, plain text body, and HTML body.
   - Parse job details (keyword, region, job count, date).
   - Collect LinkedIn job URLs.
   - Mark the message as read and move it to the configured label.
4. After processing all messages:
   - Write collected job URLs to a database.
   - Write structured jobs count to a CSV file.

Dependencies
------------
- `googleapiclient.discovery` for Gmail API access.
- Local modules:
  - `auth.get_credentials` for authentication.
  - `utils` for parsing and extraction helpers.
  - `jobs_writer` for writing job records to CSV.
  - `urls_db` for persisting job URLs.

Notes
-----
- This processor is designed specifically for LinkedIn job alert emails.
- Gmail labels must already exist in the account.
- The Gmail API must be enabled and credentials configured.
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List, cast


from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


from .auth import get_credentials
from .jobs_writer import JobRecordDict, write_job_records
from .utils import (
    decode_base64url,
    extract_job_count,
    extract_job_urls,
    extract_msg_date,
    extract_region,
    match_subject_keyword,
)
from .urls_db import write_batch


def get_message_bodies(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract plain text and HTML message bodies from a Gmail API message payload.

    Gmail messages may contain multiple MIME parts (plain text, HTML, attachments).
    This function scans the payload for `text/plain` and `text/html` parts and
    decodes them from Gmail's base64url encoding.

    Args:
        payload (Dict[str, Any]):
            The "payload" field from a Gmail message resource.

    Returns:
        Tuple[Optional[str], Optional[str]]:
            A tuple of (plain text body, HTML body). Either may be None if not present.
    """
    text_body: Optional[str] = None
    html_body: Optional[str] = None

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type: str = part.get("mimeType", "")
            body: Dict[str, Any] = part.get("body", {})
            if "data" in body:
                if mime_type == "text/plain":
                    text_body = decode_base64url(body["data"])
                elif mime_type == "text/html":
                    html_body = decode_base64url(body["data"])

    return text_body, html_body


def process_linkedin_jobs(
    account_name: str,
    label_name: str,
    csv_file_path: str,
    email_timezone: str,
    keywords: List[str],
    countries_or_regions: List[str],
) -> None:
    """
    Process unread LinkedIn job alert emails for a given Gmail account.

    Steps performed:
        1. Authenticate with Gmail using stored credentials.
        2. Query unread messages from LinkedIn job alert senders.
        3. For each message:
            - Extract subject, plain text, and HTML body.
            - Parse job details (keyword, region, job count, date).
            - Collect job URLs.
            - Mark the message as read and move it to the specified label.
        4. Write collected job URLs to a batch database.
        5. Write structured job records to a CSV file.

    Args:
        account_name (str):
            Identifier of the Gmail account (matches token_<account>.json).
        label_name (str):
            Name of the Gmail label where processed messages should be moved.
        csv_file_path (str):
            Path to the CSV file where job records will be written.
        email_timezone (str):
            Timezone string (e.g., "UTC", "Asia/Dhaka") for normalizing email dates.
        keywords (List[str]):
            List of keywords to match against job alert subjects.
        countries_or_regions (List[str]):
            List of regions to match against job alert bodies.

    Raises:
        HttpError: If a Gmail API request fails.
    """
    creds = get_credentials(account_name)

    try:
        # Build Gmail API service client
        service: Resource = build("gmail", "v1", credentials=creds)

        # Query unread LinkedIn job alert messages
        query: str = (
            "from:(jobalerts-noreply@linkedin.com OR jobs-noreply@linkedin.com) is:unread"
        )
        results: Dict[str, Any] = (
            service.users()
            .messages()
            .list(userId="me", q=query)  # , maxResults=2
            .execute()
        )
        messages: List[Dict[str, str]] = results.get("messages", [])

        if not messages:
            print(f"[{account_name}] No unread LinkedIn job alerts.")
            return

        # Fetch all labels and resolve the target label ID
        labels: List[Dict[str, str]] = (
            service.users().labels().list(userId="me").execute().get("labels", [])
        )
        label_id: Optional[str] = next(
            (lbl["id"] for lbl in labels if lbl["name"] == label_name), None
        )

        if not label_id:
            print(f"[{account_name}] Label '{label_name}' not found.")
            return

        job_details_urls: List[str] = []
        job_records: List[JobRecordDict] = []
        # Process each unread message
        for msg in messages:
            msg_id: str = msg["id"]

            # Fetch full message with headers and body
            full_msg: Dict[str, Any] = (
                service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

            # Extract subject line
            headers: List[Dict[str, str]] = full_msg["payload"]["headers"]
            subject: str = next(
                (h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)"
            )

            # Extract plain text and HTML bodies
            text_body, html_body = get_message_bodies(full_msg["payload"])
            print(f"{">" * 10}[{account_name}] Processing: '{subject}'{">" * 10}")
            if text_body:
                print(f"--- Text Body ---\n{text_body[:500]}...\n")
            if html_body:
                print(f"--- HTML Body ---\n{html_body[:500]}...\n")

            # Extract keyword from subject
            keyword: Optional[str] = None
            if subject and len(keywords) > 0:
                keyword = match_subject_keyword(subject, keywords)

            # Extract region from text or HTML body
            region: Optional[str] = None
            if text_body and countries_or_regions and len(countries_or_regions) > 0:
                region = extract_region(text_body, countries_or_regions)
            if (
                not region
                and html_body
                and countries_or_regions
                and len(countries_or_regions) > 0
            ):
                region = extract_region(html_body, countries_or_regions)

            # Extract job count from subject + body
            new_jobs_count: Optional[str] = None
            if subject and isinstance(subject, str) and text_body:
                new_jobs_count = extract_job_count(subject, text_body)
            if (
                not new_jobs_count
                and subject
                and isinstance(subject, str)
                and html_body
            ):
                new_jobs_count = extract_job_count(subject, html_body)

            # Extract email date
            email_date: Optional[str] = None
            if full_msg and email_timezone:
                email_date = extract_msg_date(
                    cast(Dict[str, Any], full_msg), email_timezone
                )
            print(
                f"[DEBUG] Keyword={keyword}, "
                f"Region={region}, "
                f"NewJobs={new_jobs_count}, "
                f"EmailDate='{email_date}'"
            )

            # If all required fields are present, build a job record
            if keyword and region and new_jobs_count and email_date:
                job_record: JobRecordDict = {
                    "keyword": keyword,
                    "country_region": region,
                    "new_jobs": new_jobs_count,
                    "date": email_date,
                }
                job_records.append(job_record)

            # Extract job detail URLs from body
            _job_details_urls: List[str] = []
            if text_body:
                _job_details_urls = extract_job_urls(text_body)
            if len(_job_details_urls) == 0 and html_body:
                _job_details_urls = extract_job_urls(html_body)
            if len(_job_details_urls) > 0:
                job_details_urls.extend(_job_details_urls)

            print(
                f"[DEBUG] Modifying message {msg_id}: "
                f"removing ['UNREAD'], adding [{label_id}]"
            )

            # Mark message as read and move to target label
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD", "INBOX"], "addLabelIds": [label_id]},
            ).execute()
            print("<" * 50)

        # After processing all messages, persist collected job URLs
        if job_details_urls and len(job_details_urls) > 0:
            print(
                f"[DEBUG] Writing {len(job_details_urls)} job detail URLs to batch output"
            )
            write_batch(job_details_urls)

        # Persist structured new job records to CSV
        if job_records and len(job_records) > 0:
            print(
                f"[DEBUG] Writing {len(job_records)} job records to CSV file: {csv_file_path}"
            )
            write_job_records(job_records, Path(csv_file_path))

        print(f"[{account_name}] All unread LinkedIn job alerts processed.")

    except HttpError as error:
        # Catch and log Gmail API errors
        print(f"[{account_name}] An error occurred: {error}")
