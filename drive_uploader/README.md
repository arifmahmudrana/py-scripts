# Drive Uploader 📂⬆️

A Python package to upload local files to Google Drive, with nested folder creation and optional local deletion.  
Run it like a CLI tool (`python -m drive_uploader`) or import its functions in your own code.

---

## Features
- Authenticate with Google Drive API (OAuth2).
- Ensure nested folder paths exist in Drive.
- Upload files matching glob patterns.
- Delete local files after upload.
- Configure multiple jobs via YAML.

**Directory structure:**
```
drive_uploader/
├── __init__.py          # Package entrypoint
├── __main__.py          # CLI entrypoint for python -m drive_uploader
├── auth.py              # OAuth2 authentication logic
├── drive_ops.py         # Folder creation and lookup utilities
├── uploader.py          # File upload and cleanup logic
├── utils.py             # Config loader and helpers
└── config.example.yaml          # Example configuration file
```

---

## Usage
1. Create a `credentials.json` in the project root (from Google Cloud Console).
2. Create a `config.yaml`:

```yaml
jobs:
  - target_path: "job-details/html"
    local_pattern: "/Users/you/py-scripts/job_details_scraper/html/*.html"

  - target_path: "reports/csv"
    local_pattern: "/Users/you/data/*.csv"

credentials_file_path: "credentials.json"
token_file_path: "token.json"
```

3. Run:
```bash
python -m drive_uploader --config config.yaml
```

---

## Importing in Python
```python
from drive_uploader import get_service, ensure_path, upload_files

service = get_service()
folder_id = ensure_path(service, "my-folder")
upload_files(service, folder_id, "./*.txt")
```
