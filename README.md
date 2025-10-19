# 🐍 py-scripts
A collection of useful Python scripts and tools for automation, data extraction, and utility tasks.  
This repository is a personal toolbox of modular Python scripts, each solving specific problems — from scraping course data to automating repetitive CLI tasks.

---

## 📦 Projects Included

### 📘 [`course_content_extractor`](./course_content_extractor)
A command-line tool to extract course curriculum from an online course platform (like Udemy) and generate a clean Markdown file.  
🔗 [Project Documentation](./course_content_extractor/README.md)

```bash
python -m course_content_extractor \
  "https://example.com/course/my-course/" \
  --curriculum-url "https://example.com/api/{course_id}/curriculum/" \
  --title-strip " | Platform"
```

---

### 📧 [`gmail_job_alerts`](./gmail_job_alerts)
Automate the processing of LinkedIn job alert emails directly from Gmail.
This tool fetches unread job alert messages, extracts structured job information, and persists them for analysis.

**Features:**

* Authenticate with Gmail via OAuth2.
* Fetch unread LinkedIn job alerts.
* Extract job details: keywords, regions, job counts, dates, and job URLs.
* Write structured job records to CSV.
* Persist LinkedIn job URLs in a local SQLite database.
* Mark processed messages as read and move them into a predefined Gmail label.

**Usage:**

```bash
python -m gmail_job_alerts --config gmail_job_alerts/config.yaml
```

**Example config (`config.yaml`):**

```yaml
csv_file_path: "jobs.csv"
email_timezone: "UTC"
accounts:
  personal: "LinkedInJobs"
keywords:
  - data engineer
countries_or_regions:
  - Germany
```

---

### 💼 [`job_details_scraper`](./job_details_scraper)

Process LinkedIn job posting URLs stored in a local SQLite database and extract structured job details.
This tool is typically run after `gmail_job_alerts`, which collects and stores job URLs.

**Features:**

* Reads job URLs from the database in configurable batch sizes.
* Fetches LinkedIn job details with retry logic (handles transient failures).
* Extracts structured fields:

  * Title, company, summary
  * Responsibilities, qualifications, benefits
  * Seniority level, employment type, job functions, industries
  * Compensation (if available)
* Saves outputs to:

  * `html/` → raw HTML snapshots
  * `text/` → human-readable summaries
* Deletes URLs from the database once processed.
* Handles termination signals (`SIGINT`, `SIGTERM`) gracefully.

**Usage:**

```bash
GJA_DB_PATH=./gmail_job_alerts/urls.db \
GJA_LOG_PATH=./gmail_job_alerts/db_failures.log \
python -m job_details_scraper
```

This will:

1. Continuously fetch up to 5 URLs at a time from the database.
2. For each URL, extract the job ID and call the scraper.
3. Save results in `job_details_scraper/html/` and `job_details_scraper/txt/`.
4. Delete processed URLs from the database.
5. Exit when no URLs remain or the user presses `Ctrl+C`.

---

### 📂 `drive_uploader`

A command-line utility to upload local files to Google Drive with support for nested folder creation and automatic cleanup.  
It reads a YAML configuration file containing multiple upload jobs, each specifying a local file pattern and a target Drive path.

**Features:**
- Authenticate with Google Drive using OAuth2.
- Ensure nested folder paths exist (like `mkdir -p`).
- Upload files matching glob patterns (e.g. `*.html`, `**/*.csv`).
- Optionally delete local files after upload.
- Configure multiple jobs via a single YAML file.

**Usage:**
```bash
python -m drive_uploader --config drive_uploader/config.yaml
```

**Example config:**
```yaml
jobs:
  - target_path: "job-details/html"
    local_pattern: "/path/to/html/*.html"

  - target_path: "reports/csv"
    local_pattern: "/path/to/reports/**/*.csv"

credentials_file_path: "credentials.json"
token_file_path: "token.json"
```

**Importable API:**
```python
from drive_uploader import get_service, ensure_path, upload_files

service = get_service()
folder_id = ensure_path(service, "my-folder")
upload_files(service, folder_id, "./*.txt")
```

This module is useful for automating file uploads to Google Drive from local scripts or pipelines. It can be run as a standalone CLI tool or integrated into other Python projects.

---

### 🗂️ [`file_merger`](./file_merger)

A lightweight Python package/CLI tool to merge multiple files into one, with configurable **prefix**, **join string**, **suffix**, and a **final string appended once at the end**.  
Configuration is provided via a YAML file, while file paths are passed as command-line arguments.  
🔗 [Project Documentation](./file_merger/README.md)

**Usage:**

1. Create a `config.yml` file:

```yaml
first_prepend: "---AT THE BEGINNING---\n"
prefix: "---START---\n"
join: "\n---NEXT FILE---\n"
suffix: "\n---END---\n"
final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"
output_path: "merged_output.txt"
```

2. Run the tool:

```bash
python -m file_merger -c config.yml file1.txt file2.txt file3.txt
```

This will produce `merged_output.txt` with:
- A string (`first_prepend`) appended once at the very beginning
- Each file wrapped in `prefix` and `suffix`
- Files separated by `join`
- A final string (`final_append`) appended once at the very end

---

### 🗃️ [`file_merger_batch`](./file_merger_batch)
A companion tool to `file_merger` that merges files in **batches** using a glob pattern.  
Instead of listing files manually, you provide a pattern (e.g. `a/*.txt`) and configure two processing groups:
1. **First file(s)**: Process the first N files separately with custom formatting
2. **Rest files**: Process remaining files in batches with a different configuration

🔗 [Project Documentation](./file_merger_batch/README.md)

**Example config (`config.yml`):**

```yaml
files: "a/*.txt"
first_file:
  first_prepend: "---AT THE BEGINNING---\n"
  prefix: "---START---\n"
  join: "\n---NEXT FILE---\n"
  suffix: "\n---END---\n"
  final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"
  output_path: "b/c/"
  output_file_name_pattern: "abc.txt"
  size: 5
rest_files:
  first_prepend: "---AT THE BEGINNING---\n"
  prefix: "---START---\n"
  join: "\n---NEXT FILE---\n"
  suffix: "\n---END---\n"
  final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"
  output_path: "b/c/"
  output_file_name_pattern: "abc[batch].txt"
  chunk_size: 5
```

**Usage:**

```bash
python -m file_merger_batch -c config.yml
```

This will:
- Expand the glob pattern (`a/*.txt`)
- Process the first 5 files into `b/c/abc.txt` using `first_file` configuration
- Split remaining files into chunks of 5
- Merge each chunk into separate files (`b/c/abc1.txt`, `b/c/abc2.txt`, …) using `rest_files` configuration
- Apply respective formatting for each group

---

### 🔗 [`url_extractor`](./url_extractor)
Extract URLs from a file, filter by domain, and save results into a file. Supports removing duplicate with original order.  
🔗 [Project Documentation](./url_extractor/README.md)

**Example config (`config.yml`):**

```yaml
# config.yaml
input_text_file: "/path/to/source.txt"        # path to the text file to scan
output_file: "/path/to/output_urls.txt"       # where to write extracted URLs
domain_filter: "www.udemy.com"                # domain to keep (exact or substring)
unique_only: true                             # true => write only unique URLs
```

**Usage:**

```bash
python -m url_extractor -c config.yml
```

This will:
- Read the file `/path/to/source.txt` and extract http/https URLs
- Filter URLs by `www.udemy.com` (substring match)
- Finds unique URLs (preserves original order)
- Writes URLs to `/path/to/output_urls.txt`

---

### 🔧 [`yaml_setter`](./yaml_setter)

A simple Python utility to set values in YAML files using dot notation paths with array index support.  
Read content from any file and insert it at a specific path in a YAML file, creating nested structures automatically.  
🔗 [Project Documentation](./yaml_setter/README.md)

**Features:**
- Set values using dot notation (e.g., `a.b.c`)
- Support for array indices (e.g., `users[0].name`)
- Support for multi-dimensional arrays (e.g., `matrix[0][7]`)
- Automatically creates missing directories and nested structures
- Preserves existing YAML content
- Clean YAML formatting

**Usage:**

```bash
# Simple nested path
python -m yaml_setter data.txt config.yaml "database.connection.host"

# Array index
python -m yaml_setter message.txt config.yaml "notifications[0].message"

# Multi-dimensional array
python -m yaml_setter content.md config.yaml "matrix[2][5].data"

# Complex nested structure
python -m yaml_setter readme.md config.yaml "docs.api[0].examples[3].code"
```

**As a Library:**

```python
from yaml_setter import set_yaml_value

# Set a simple value
set_yaml_value("config.yaml", "app.name", "My Application")

# Set value with array index
set_yaml_value("config.yaml", "users[0].email", "user@example.com")

# Set value in multi-dimensional array
content = "Hello World"
set_yaml_value("data.yaml", "grid[5][10]", content)
```

**Path Syntax Examples:**
```
a.b.c           →  {a: {b: {c: value}}}
a.b[0]          →  {a: {b: [value]}}
a[0].b          →  {a: [{b: value}]}
a[0][1]         →  {a: [[null, value]]}
users[0].name   →  {users: [{name: value}]}
```

---

## 🧰 Requirements

* Python 3.12.3 or higher
* Use `pip` to install dependencies

```bash
pip install -r requirements.txt
```

Or, if you use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📁 Directory Structure

```
py-scripts/
│
├── course_content_extractor/   # Course extraction CLI tool
│   ├── __main__.py
│   ├── extractor.py
│   ├── helpers.py
│   ├── models.py
│   └── README.md
│
├── gmail_job_alerts/           # Gmail LinkedIn job alerts automation
│   ├── __init__.py
│   ├── __main__.py
│   ├── auth.py
│   ├── processor.py
│   ├── utils.py
│   ├── jobs_writer.py
│   ├── urls_db.py
│   ├── README.md
│   └── config.example.yaml (example)
│
├── job_details_scraper/        # LinkedIn job details scraper
│   ├── __init__.py
│   ├── __main__.py
│   ├── job_url_processor.py
│   ├── linkedin_scraper.py
│   ├── README.md
│   └── retry_utils.py
│
├── drive_uploader/        # Drive Uploader(Google for now)
│   ├── __init__.py
│   ├── __main__.py
│   ├── auth.py
│   ├── drive_ops.py
│   ├── uploader.py
│   ├── utils.py
│   ├── README.md
│   └── config.example.yaml
│
├── file_merger/        # Merge files into one
│   ├── __init__.py
│   ├── __main__.py
│   ├── merger.py
│   ├── config.example.yml
│   └── README.md
│
├── file_merger_batch/   # Merge files batch
│   ├── __init__.py
│   ├── __main__.py
│   ├── batch_merger.py
│   ├── config.example.yml
│   └── README.md
│
├── url_extractor/   # Extract URLs from file
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── core.py
│   ├── config.example.yml
│   └── README.md
│
├── yaml_setter/   # Set values in YAML files
│   ├── __init__.py
│   ├── __main__.py
│   ├── yaml_setter.py
│   └── README.md
│
├── .gitignore
└── README.md
```

---

## 📜 License

This repository is licensed under the [BSD 3-Clause License](./LICENSE).

---

## ✨ Contributing

Suggestions, improvements, and pull requests are welcome!
If you have your own useful script, feel free to contribute it as a module under this repo.

---

## 🙌 Acknowledgments

Some tools may reference or be inspired by public platform structures (like Udemy or LinkedIn).
This repo is intended for **personal and educational** use only. Please respect the terms of service of any third-party platform you interact with.
