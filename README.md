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
- Authenticate with Gmail via OAuth2.
- Fetch unread LinkedIn job alerts.
- Extract job details: keywords, regions, job counts, dates, and job URLs.
- Write structured job records to CSV.
- Persist LinkedIn job URLs in a local SQLite database.
- Mark processed messages as read and move them into a predefined Gmail label.

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
│   └── config.yaml (example)
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
