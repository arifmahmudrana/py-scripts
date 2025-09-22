"""
File upload utilities.
"""

import os
import glob
from googleapiclient.http import MediaFileUpload


def upload_files(service, folder_id: str, pattern: str, delete_local: bool = True):
    """
    Upload files matching a glob pattern to a Drive folder.

    Args:
        service: Drive API service.
        folder_id: Target Drive folder ID.
        pattern: Glob pattern for local files.
        delete_local: If True, delete local files after upload.
    """
    for filepath in glob.glob(pattern):
        filename = os.path.basename(filepath)
        file_metadata = {"name": filename, "parents": [folder_id]}
        media = MediaFileUpload(filepath, resumable=True)
        uploaded = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"⬆️ Uploaded: {filename} (ID: {uploaded['id']})")
        if delete_local:
            os.remove(filepath)
            print(f"🗑️ Deleted local file: {filepath}")
