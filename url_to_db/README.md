# 🔗➡️💾 url_to_db

Extract URLs from a text file and write them directly to the SQLite database.

This module combines `url_extractor` functionality with `gmail_job_alerts` database operations
to provide a simple pipeline: **text file → URL extraction → database**.

---

## Features
- Read text file and extract http/https URLs
- Filter URLs by domain (substring match)
- Optionally keep only unique URLs (preserves original order)
- Write URLs directly to SQLite database
- Usable as a module: `python -m url_to_db -c config.yaml`

---

## 📂 Project Structure
```
url_to_db/
├── __init__.py
├── __main__.py
├── cli.py
├── core.py
├── config.example.yml
└── README.md
```

---

## 🚀 Usage

### Command Line
```bash
cd py-scripts
python -m url_to_db -c ./url_to_db/config.yaml
```

### As a Python Module
```python
from url_to_db.core import process_urls_to_db

# Process URLs and write to database
count = process_urls_to_db("./url_to_db/config.yaml")
print(f"Processed {count} URLs")
```

---

## ⚙️ Configuration (YAML)

Create a `config.yaml` file:
```yaml
# Input text file containing URLs
input_text_file: "url_extractor/source.txt"

# Domain to filter URLs (substring match, case-insensitive)
domain_filter: "www.udemy.com"

# Strip query parameters from URLs before processing (optional, default: false)
strip_query_params: true

# Only process unique URLs (preserves original order)
unique_only: true
```

### Config Options:

- **input_text_file**: Path to text file containing URLs (required)
- **domain_filter**: Domain substring to filter URLs (required)
- **strip_query_params**: Remove query parameters from URLs before deduplication (optional, default: false)
- **unique_only**: If true, only unique URLs are written (required)

---

## 🔄 How It Works

1. **Extract**: Reads the input text file and extracts all http/https URLs
2. **Filter**: Filters URLs by the specified domain (case-insensitive substring match)
3. **Strip** (optional): Removes query parameters from URLs (e.g., `?foo=bar&baz=qux`)
4. **Deduplicate**: If `unique_only` is true, removes duplicate URLs while preserving order
5. **Persist**: Writes URLs to the SQLite database (`gmail_job_alerts/urls.db`)

The database operations automatically:
- Ignore duplicate URLs (enforced by PRIMARY KEY)
- Create the database if it doesn't exist
- Log any failures to `gmail_job_alerts/db_failures.log`

---

## 📊 Example Workflow
```bash
# 1. Create a source file with URLs (some with query params)
echo "Check out https://www.udemy.com/course/python-basics/?couponCode=ABC123" > source.txt
echo "Also https://www.udemy.com/course/python-basics/?couponCode=XYZ789" >> source.txt
echo "And https://www.udemy.com/course/web-dev/" >> source.txt
echo "Plus https://example.com/other?param=value" >> source.txt

# 2. Create config
cat > config.yaml << EOF
input_text_file: "source.txt"
domain_filter: "www.udemy.com"
strip_query_params: true
unique_only: true
EOF

# 3. Process URLs to database
python -m url_to_db -c config.yaml

# Output:
# Extracted 4 URLs from file
# Filtered to 3 URLs matching domain: www.udemy.com
# Stripped query parameters from URLs
# Kept 2 unique URLs
# Wrote 2 URLs to database
# Successfully processed 2 URLs to database.
```

In this example:
- Both `https://www.udemy.com/course/python-basics/?couponCode=ABC123` and `https://www.udemy.com/course/python-basics/?couponCode=XYZ789` become `https://www.udemy.com/course/python-basics/`
- After deduplication, only one instance is kept
- The example.com URL is filtered out by domain

---

## 🔗 Related Modules

This module integrates functionality from:

- **url_extractor**: For extracting and filtering URLs from text files
- **gmail_job_alerts**: For database operations (urls_db.py)

You can use these modules independently or combine them as needed:
```bash
# Extract URLs to file
python -m url_extractor -c config.yaml

# Or extract URLs to database (this module)
python -m url_to_db -c config.yaml
```

---

## 🗄️ Database Details

URLs are stored in: `gmail_job_alerts/urls.db`

The database schema is simple:
```sql
CREATE TABLE urls (
    url TEXT PRIMARY KEY
)
```

You can read and process URLs from the database using:
```python
from gmail_job_alerts import read_urls, delete_urls

# Read URLs
for url in read_urls(limit=10):
    print("Processing:", url)
    # ... do something ...
    delete_urls(url)  # remove after processing
```

---

## 📝 Notes

- The database path defaults to `./gmail_job_alerts/urls.db` but can be overridden with the `GJA_DB_PATH` environment variable
- Failed database operations are logged to `./gmail_job_alerts/db_failures.log`
- URLs are automatically deduplicated by the database (PRIMARY KEY constraint)
- The module preserves original URL order when `unique_only` is true

---

## ⚠️ Requirements

- Python 3.12.3 or higher
- PyYAML
- url_extractor module
- gmail_job_alerts module

See the main project README for installation instructions.
