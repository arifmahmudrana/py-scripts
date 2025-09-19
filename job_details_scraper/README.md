# Job Details Scraper

`job_details_scraper` is a Python package for **fetching and parsing job postings from LinkedIn**.
It is designed to run as a module (via `python -m job_details_scraper`), continuously pulling job URLs from a local SQLite database, scraping job details, and storing structured outputs.

---

## Features

* ✅ Continuous batch processing of LinkedIn job posting URLs
* ✅ Safe retry logic with exponential backoff for flaky network calls
* ✅ Structured extraction of job details:

  * Title, company, summary, responsibilities, qualifications, benefits
  * Seniority level, employment type, job functions, industries
  * Compensation information (if present)
* ✅ Saves both:

  * Raw HTML (`html/`)
  * Human-readable structured text (`text/`)
* ✅ Graceful handling of termination signals (`SIGINT`, `SIGTERM`)
* ✅ Modular design — scraper functions can be reused independently

---

## Project Structure

```
job_details_scraper/
│
├── __init__.py          # Package initializer, exports retry decorator
├── __main__.py          # Entry point when running `python -m job_details_scraper`
├── job_url_processor.py # Batch processor for job URLs from database
├── linkedin_scraper.py  # Core LinkedIn scraping and parsing utilities
└── retry_utils.py       # Exponential backoff retry decorator
```

---

## Environment Variables

Although `__main__.py` does not consume environment variables directly, other modules depend on the following being set before execution:

* **`GJA_DB_PATH`**
  Path to the SQLite database file (`urls.db`) containing job URLs.
  Example: `./gmail_job_alerts/urls.db`

* **`GJA_LOG_PATH`**
  Path to the log file used by related modules.
  Example: `./gmail_job_alerts/db_failures.log`

---

## Usage

### Running as a Module

Run the scraper by setting environment variables and executing:

```sh
GJA_DB_PATH=./gmail_job_alerts/urls.db \
GJA_LOG_PATH=./gmail_job_alerts/db_failures.log \
python -m job_details_scraper
```

### Execution Flow

1. The processor fetches job URLs from the database in batches (`batch_size=5` by default).
2. For each URL:

   * Extracts the job ID
   * Calls `get_job_details_from_url` (with retry logic)
   * Saves raw HTML to `html/{job_id}.html`
   * Saves structured text summary to `text/{job_id}.txt`
3. Deletes processed URLs from the database.
4. Stops when no URLs remain or when interrupted (`Ctrl+C`).

---

## Modules

### `job_url_processor.py`

* Handles the main processing loop:

  * Reads URLs from DB (via `gmail_job_alerts.read_urls`)
  * Calls the LinkedIn scraper
  * Deletes processed URLs
* Responds to termination signals gracefully.
* Exposes `process_all_job_urls()` for external use.

### `linkedin_scraper.py`

* Provides `get_job_details_from_url()` for fetching and parsing job pages.
* Extracts:

  * Job title, company, summary, responsibilities, qualifications, benefits
  * Seniority, employment type, functions, industries, compensation info
* Saves both raw HTML and structured `.txt` output.
* Uses BeautifulSoup for HTML parsing.

### `retry_utils.py`

* Defines `exponential_backoff_retry` decorator.
* Retries failed function calls with exponential backoff + jitter.
* Useful for handling transient network or scraping errors.

### `__main__.py`

* Package entry point when run as `python -m job_details_scraper`.
* Configures fixed output directories:

  * `html/` (for raw HTML)
  * `text/` (for parsed summaries)
* Calls `process_all_job_urls()` and handles top-level errors.

### `__init__.py`

* Exports only `exponential_backoff_retry` at package level.
* Provides high-level documentation of the package purpose.

---

## Example Workflow

1. Populate `urls.db` with LinkedIn job posting URLs (via `gmail_job_alerts`).

2. Run the scraper:

   ```sh
   GJA_DB_PATH=./gmail_job_alerts/urls.db \
   GJA_LOG_PATH=./gmail_job_alerts/db_failures.log \
   python -m job_details_scraper
   ```

3. Outputs:

   * `job_details_scraper/html/{job_id}.html` — raw HTML snapshot
   * `job_details_scraper/text/{job_id}.txt` — human-readable structured job details

---

## Development

### Linting & Code Style

* Follows **PEP 8** with Flake8 and Pylint checks.
* Long lines suppressed with `# noqa: E501` where needed.
* Broad exception catches are explicitly marked with
  `# pylint: disable=broad-exception-caught`.

### Dependencies

* `requests` — HTTP requests
* `beautifulsoup4` — HTML parsing
* `gmail_job_alerts` — database interaction (external module)

### Testing Retry Logic

You can test `retry_utils` standalone:

```sh
python job_details_scraper/retry_utils.py
```

This runs example functions with retries and demonstrates behavior.
