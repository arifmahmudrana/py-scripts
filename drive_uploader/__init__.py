"""
Drive Uploader Package
======================

This package provides utilities to upload local files to Google Drive.
It is designed to be run as a command-line tool (`python -m drive_uploader`)
but also exposes reusable functions for other Python code.

Main features:
- Authenticate with Google Drive API (OAuth2 user flow).
- Ensure nested folder paths exist in Drive.
- Upload files matching local glob patterns.
- Delete local files after upload (optional).
- Configure multiple upload jobs via a YAML file.
"""

from .auth import get_service
from .drive_ops import ensure_path
from .uploader import upload_files
from .utils import load_config

__all__ = ["get_service", "ensure_path", "upload_files", "load_config"]
