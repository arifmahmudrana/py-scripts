"""
Authentication utilities for Google Drive API.
"""

import os
from typing import Optional
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_credentials(
    credentials_file: str = "credentials.json", token_file: str = "token.json"
) -> Credentials:
    """
    Load or obtain OAuth2 credentials for Google Drive API.

    Args:
        credentials_file: Path to OAuth client secrets JSON.
        token_file: Path to cached token JSON.

    Returns:
        Credentials object.
    """
    creds: Optional[Credentials] = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


def get_service(
    credentials_file: str = "credentials.json", token_file: str = "token.json"
):
    """
    Build an authenticated Google Drive API service.

    Args:
        credentials_file: Path to OAuth client secrets JSON.
        token_file: Path to cached token JSON.

    Returns:
        Drive API service instance.
    """
    creds = get_credentials(credentials_file, token_file)
    return build("drive", "v3", credentials=creds)
