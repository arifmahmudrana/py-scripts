# 📘 Course Content Extractor

A Python CLI tool that fetches the course curriculum from an online course platform and generates a structured Markdown file.

> Ideal for archiving or auditing course outlines from sites like Udemy (or similar platforms that expose curriculum data via HTML + API).

---

## 🚀 Features

- Extracts **course title** and **ID** from the course landing page
- Fetches full **curriculum structure** (sections and items) via the platform's API
- Outputs a clean, readable **Markdown file**
- Fully configurable API and parsing via CLI arguments
- Supports **custom title suffix stripping**
- Designed for extensibility and scriptability

---

## 🧰 Requirements

- Python 3.12.3+
- Dependencies:
  - `requests`
  - `beautifulsoup4`
  - `jinja2`

You can install the dependencies via:

```bash
pip install -r requirements.txt
````

---

## 📦 Installation

Clone the repo:

```bash
git clone https://github.com/arifmahmudrana/py-scripts.git
cd py-scripts
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧪 Usage

You can run the module directly using:

```bash
python -m course_content_extractor \
  "https://example.com/course/python-basics/" \
  --curriculum-url "https://example.com/{course_id}/abc/" \
  --title-strip " | Example"
```

### 💡 CLI Options

| Argument                | Description                                                 |
| ----------------------- | ----------------------------------------------------------- |
| `course_url`            | URL of the course landing page *(required)*                 |
| `--curriculum-url, -cu` | API URL pattern with `{course_id}` placeholder *(required)* |
| `--title-strip, -ts`    | Optional suffix to remove from course title                 |

---

## 🧱 Project Structure

```text
course_content_extractor/
│
├── __main__.py         # CLI entry point
├── extractor.py        # Core logic
├── helpers.py          # Utility functions and templates
├── models.py           # TypedDict models for API and template context
└── README.md
```

---

## 📝 Output Format

The extracted Markdown file is saved as:

```bash
<normalized-course-title>.md
```

Sample output:

```markdown
# Python Basics for Beginners

- Introduction
  - Welcome
  - How This Course Works

- Getting Started
  - Installing Python
  - Writing Your First Script

...
```

---

## ✨ Customization

You can modify the Markdown output structure by editing the default Jinja2 template in [`helpers.py`](course_content_extractor/helpers.py):

```python
DEFAULT_TEMPLATE = """
# {{ course.title }}

{% for section in sections %}
- {{ section.title }}

  {% for item in section.items %}
  - {{ item.title }}
    {{ item.description | replace('\n', '') }}
  {% endfor %}

{% endfor %}
"""
```

---

## ⚠️ Disclaimer

This tool is intended for educational or internal use only. Ensure that you comply with the terms of service of any platform you extract content from.
