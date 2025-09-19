"""
LinkedIn Job Scraper Utilities.

This module provides functions to fetch, parse, and extract structured job
details from LinkedIn job posting pages. The extracted information includes
title, company, description sections (summary, responsibilities, qualifications,
benefits), job criteria (seniority level, employment type, job functions,
industries), and compensation information.

Additionally, the module saves the raw HTML and a human-readable text dump
for each processed job posting.
"""

from http import HTTPStatus
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import requests
from bs4 import BeautifulSoup, Tag

from .retry_utils import exponential_backoff_retry


# Default HTTP headers used when fetching LinkedIn job pages
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

# Mapping of common section aliases to standardized keys
SECTION_ALIASES = {
    "what you'll do": "responsibilities",
    "responsibilities": "responsibilities",
    "what we look for": "qualifications",
    "requirements": "qualifications",
    "qualifications": "qualifications",
    "what we offer": "benefits",
    "benefits": "benefits",
}


def _clean_text(s: str) -> str:
    """
    Normalize text by collapsing whitespace and stripping leading/trailing spaces.
    """
    return re.sub(r"\s+", " ", s).strip()


def _text_with_newlines(el: Tag) -> str:
    """
    Extract text content from an HTML element, converting <br> tags into newlines.

    Args:
        el: A BeautifulSoup Tag representing an HTML element.

    Returns:
        Cleaned text with normalized whitespace and line breaks.
    """
    if el is None:
        return ""

    el = BeautifulSoup(str(el), "html.parser")
    for br in el.find_all("br"):
        br.replace_with("\n")

    return "\n".join(
        [line.strip() for line in el.get_text("\n").splitlines() if line.strip()]
    )


def _extract_job_criteria(details_root: Tag) -> Dict[str, Any]:
    """
    Extract job criteria (seniority, employment type, job functions, industries)
    from a LinkedIn job posting.

    Args:
        details_root: The BeautifulSoup root element containing job details.

    Returns:
        A dictionary with keys:
            - "seniority_level" (str or None)
            - "employment_type" (str or None)
            - "job_functions" (list[str])
            - "industries" (list[str])
    """
    out = {
        "seniority_level": None,
        "employment_type": None,
        "job_functions": [],
        "industries": [],
    }

    ul = details_root.select_one("ul.description__job-criteria-list")
    if not ul:
        return out

    for li in ul.select("li.description__job-criteria-item"):
        header = li.select_one("h3.description__job-criteria-subheader")
        value = li.select_one("span.description__job-criteria-text")
        htext = _clean_text(header.get_text()) if header else ""
        vtext = _clean_text(value.get_text()) if value else ""

        if not htext:
            continue

        key = htext.lower()
        if "seniority" in key:
            out["seniority_level"] = vtext or None
        elif "employment" in key:
            out["employment_type"] = vtext or None
        elif "job function" in key:
            out["job_functions"] = (
                [x.strip() for x in vtext.split(" and ") if x.strip()] if vtext else []
            )
        elif "industr" in key:
            parts = re.split(r",|/| and ", vtext)
            out["industries"] = [p.strip() for p in parts if p.strip()]

    return out


def _extract_description_sections(details_root: Tag) -> Dict[str, Any]:
    """
    Extract structured description sections (summary, responsibilities,
    qualifications, benefits) from a job posting.

    Args:
        details_root: The BeautifulSoup root element containing job details.

    Returns:
        A dictionary with keys:
            - "summary": str
            - "responsibilities": list[str]
            - "qualifications": list[str]
            - "benefits": list[str]
    """
    result = {
        "summary": "",
        "responsibilities": [],
        "qualifications": [],
        "benefits": [],
    }

    desc_root = details_root.select_one(
        "div.description__text--rich, div.description__text"
    )
    if not desc_root:
        return result

    rich = desc_root.select_one(".show-more-less-html__markup") or desc_root

    def normalize_header(text: str) -> str:
        t = _clean_text(re.sub(r"[:\-\–]+$", "", text.lower()))
        t = re.sub(r"\s+", " ", t)
        return SECTION_ALIASES.get(t, t)

    sections: List[tuple[str, List[str]]] = []
    current_header: Optional[str] = None
    before_first_header_chunks: List[str] = []

    # Replace <br> with newlines
    for br in rich.find_all("br"):
        br.replace_with("\n")

    # Traverse children nodes
    for node in rich.contents:
        # Detect strong-tag headers
        if isinstance(node, Tag) and node.name == "strong":
            header_key = normalize_header(node.get_text(separator=" ").strip())
            current_header = header_key
            sections.append((current_header, []))

            # Look for immediate <ul> following header
            ul = node.find_next(lambda t: isinstance(t, Tag) and t.name == "ul")
            if ul:
                items = [
                    _clean_text(_text_with_newlines(li)) for li in ul.find_all("li")
                ]
                items = [x for x in items if x]
                sections[-1] = (current_header, items)
            continue

        # Handle bullet lists under the current header
        if isinstance(node, Tag) and node.name == "ul" and current_header:
            items = [_clean_text(_text_with_newlines(li)) for li in node.find_all("li")]
            items = [x for x in items if x]
            sections[-1] = (sections[-1][0], sections[-1][1] + items)
        else:
            # Collect summary text before first header
            if not sections:
                text = (
                    _text_with_newlines(node)
                    if isinstance(node, Tag)
                    else str(node).strip()
                )
                text = _clean_text(text)
                if text:
                    before_first_header_chunks.append(text)

    if before_first_header_chunks:
        result["summary"] = "\n\n".join(before_first_header_chunks)

    for key, items in sections:
        if key in ("responsibilities", "qualifications", "benefits"):
            result[key] = items

    return result


def _extract_compensation(details_root: Tag) -> Dict[str, Optional[str]]:
    """
    Extract compensation information from a LinkedIn job posting.

    Args:
        details_root: The BeautifulSoup root element containing job details.

    Returns:
        A dictionary with keys:
            - "compensation_title": str or None
            - "compensation_description": str or None
            - "salary_range": str or None
    """
    comp_section = details_root.select_one("section.compensation")
    if not comp_section:
        return {}

    title = comp_section.select_one("h2")
    description = comp_section.select_one("p.compensation__description")
    salary = comp_section.select_one(".compensation__salary")

    return {
        "compensation_title": _clean_text(title.get_text()) if title else None,
        "compensation_description": (
            _clean_text(description.get_text()) if description else None
        ),
        "salary_range": _clean_text(salary.get_text()) if salary else None,
    }


@exponential_backoff_retry(
    max_retries=3, base_delay=2, exceptions_to_retry=(requests.HTTPError,)
)
def get_job_details_from_url(
    url: str,
    job_id: str,
    timeout: int = 20,
    html_dir: Optional[Path] = None,
    txt_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Fetch and extract structured job details from a LinkedIn job posting URL.

    Side effects:
        - Saves the raw HTML to <html_dir>/<job_id>.html
        - Saves a human-readable .txt summary to <txt_dir>/<job_id>.txt

    Args:
        url: The LinkedIn job posting URL.
        job_id: Unique job identifier (used for filenames).
        timeout: Request timeout in seconds (default: 20).
        html_dir: Optional directory path where raw HTML will be saved.
                  Defaults to current working directory.
        txt_dir: Optional directory path where human-readable .txt summary will be saved.
                 Defaults to current working directory.

    Returns:
        A dictionary containing job metadata and structured information.
    """
    # Fetch HTML
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    if r.status_code == HTTPStatus.NOT_FOUND:
        return {
            "Error": "Job not found",
            "Source URL": url,
        }
    r.raise_for_status()
    html_content = r.text

    # Build save paths
    html_dir = html_dir or Path(".")
    txt_dir = txt_dir or Path(".")

    html_path = html_dir / f"{job_id}.html"
    txt_path = txt_dir / f"{job_id}.txt"

    # Ensure dirs exist
    html_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)

    # Save raw HTML
    with html_path.open("w", encoding="utf-8") as f:
        f.write(html_content)

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract job title
    title_tag = soup.find("h1")
    title = _clean_text(title_tag.get_text()) if title_tag else None

    # Extract details root
    details = soup.select_one("div.decorated-job-posting__details") or soup

    # Extract description, criteria, compensation
    desc = _extract_description_sections(details)
    criteria = _extract_job_criteria(details)
    compensation = _extract_compensation(details)

    # Extract company name
    company = None
    possible_company = soup.select_one(
        "[data-company-name], a.topcard__org-name-link, span.topcard__flavor"
    )
    if possible_company:
        company = _clean_text(possible_company.get_text())

    # Collect cleaned text dump
    clean_text_dump = _text_with_newlines(details)

    # Construct structured data
    data = {
        "Title": title,
        "Company": company,
        "Summary": desc.get("summary") or None,
        "Responsibilities": desc.get("responsibilities", []),
        "Qualifications": desc.get("qualifications", []),
        "Benefits": desc.get("benefits", []),
        "Seniority level": criteria.get("seniority_level"),
        "Employment type": criteria.get("employment_type"),
        "Job functions": criteria.get("job_functions", []),
        "Industries": criteria.get("industries", []),
        "Compensation": compensation or None,
        "Source URL": url,
    }

    # Save human-readable .txt
    with txt_path.open("w", encoding="utf-8") as f:
        f.write("=== Job Metadata ===\n")
        for key, value in data.items():
            if not value:
                continue
            if isinstance(value, list):
                f.write(f"{key}:\n")
                for item in value:
                    f.write(f"  - {item}\n")
            elif isinstance(value, dict):
                f.write(f"{key}:\n")
                for subk, subv in value.items():
                    f.write(f"  {subk}: {subv}\n")
            else:
                f.write(f"{key}: {value}\n")
        f.write("\n=== Full Cleaned Job Details Text ===\n")
        f.write(clean_text_dump)

    return data
