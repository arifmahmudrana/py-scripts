"""
Drive operations: find, create, and ensure folders.
"""


def find_folder_id(service, name, parent_id=None):
    """Find folder ID by name, optionally within a parent."""
    if parent_id:
        query = f"name = '{name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    else:
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def create_folder(service, name, parent_id=None):
    """Create a folder, optionally inside a parent."""
    metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadata["parents"] = [parent_id]
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def ensure_path(service, path: str) -> str:
    """
    Ensure nested folders exist like mkdir -p, return final folder ID.
    """
    parts = path.strip("/").split("/")
    parent_id = None
    for part in parts:
        folder_id = find_folder_id(service, part, parent_id)
        if not folder_id:
            folder_id = create_folder(service, part, parent_id)
            print(f"📂 Created folder: {part} (ID: {folder_id})")
        else:
            print(f"✅ Found folder: {part} (ID: {folder_id})")
        parent_id = folder_id
    return parent_id
