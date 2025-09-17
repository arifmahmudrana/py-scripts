"""
Authentication Utilities for Gmail Job Alerts
=============================================

This module provides helper functions to authenticate with the Gmail API
using OAuth 2.0. It ensures that credentials are securely stored and reused
for subsequent runs of the Gmail Job Alerts automation.

Overview
--------
- Uses Google's OAuth 2.0 flow to obtain user credentials.
- Stores credentials in a token file (`token_<account_name>.json`) so that
  the user does not need to re‑authenticate every time.
- Refreshes expired credentials automatically if a refresh token is available.
- Falls back to launching a local server for interactive login if no valid
  credentials are found.

Scopes
------
The Gmail API scope used here is:

    https://www.googleapis.com/auth/gmail.modify

This scope allows:
    - Reading messages
    - Modifying labels
    - Marking messages as read/unread

It does **not** allow sending email or full account access.

Credential Files
----------------
- **credentials.json**: OAuth 2.0 client secrets file downloaded from
  Google Cloud Console. Must be placed in the `gmail_job_alerts/` directory.
- **token_<account_name>.json**: Generated automatically after the first
  successful login. Stores the user's access and refresh tokens for the
  given account.

Usage
-----
Typical usage within the project:

```python
from gmail_job_alerts.auth import get_credentials
from googleapiclient.discovery import build

creds = get_credentials("personal")
service = build("gmail", "v1", credentials=creds)

# Now you can call Gmail API methods, e.g.:
results = service.users().labels().list(userId="me").execute()
```

Error Handling
--------------
- If `credentials.json` is missing or invalid, the OAuth flow will fail.
- If the token file is corrupted, it will be ignored and a new login flow
  will be triggered.

Notes
-----
- Each account should have its own token file, distinguished by the
  `account_name` argument.
- The first run will open a browser window for Google login and consent.
- Subsequent runs will use the stored token until it expires or is revoked.
"""

import os
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail scope: read, modify labels, mark messages read/unread
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_credentials(account_name: str) -> Credentials:
    """
    Load or refresh Gmail API credentials for a given account.

    This function attempts to load stored credentials from a token file.
    If the credentials are missing, expired, or invalid, it will either:
      - Refresh them automatically (if a refresh token is available), or
      - Launch an interactive OAuth 2.0 flow in the browser to obtain new ones.

    The resulting credentials are saved back to the token file for reuse.

    Args:
        account_name (str):
            Identifier for the Gmail account (e.g., "personal", "work").
            Determines the name of the token file:
            `token_<account_name>.json`.

    Returns:
        Credentials:
            A valid `google.oauth2.credentials.Credentials` object that can
            be used to build a Gmail API service client.

    Raises:
        FileNotFoundError:
            If the `credentials.json` file is missing when a new login flow
            is required.
    """
    token_file = f"./gmail_job_alerts/token_{account_name}.json"
    creds: Optional[Credentials] = None

    # Load existing credentials if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # If no valid credentials, refresh or initiate login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./gmail_job_alerts/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for next time
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds
