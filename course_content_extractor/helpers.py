"""
Helpers for Course Content Extractor

This module contains helper functions and templates used for extracting and
 formatting course content into markdown.
It includes utilities for normalizing filenames and
 generating the default markdown template.
"""

import re


def normalize_filename(title: str) -> str:
    """
    Normalize a course title for use as a filename.

    This function cleans up the title by removing special characters,
    HTML tags, and replacing spaces/underscores with a single underscore.
    It also limits the filename to a maximum of 100 characters.

    Args:
        title (str): The course title to normalize.

    Returns:
        str: A sanitized version of the title suitable for use as a filename.

    Example:
        (
            "Complete Course: Introduction & Basics/Section 1"
            -> "Complete_Course_Introduction_Basics_Section_1"
        )
    """
    # Remove HTML tags if any
    title = re.sub(r"<[^>]+>", "", title)
    # Replace special characters with underscores
    title = re.sub(r'[<>:"/\\|?*]', "_", title)
    # Replace multiple spaces/underscores with a single underscore
    title = re.sub(r"[_\s]+", "_", title)
    # Remove leading/trailing underscores
    title = title.strip("_")
    # Limit length to 100 characters
    if len(title) > 100:
        title = title[:100]
    return title


# Default Jinja2 template for generating course markdown
DEFAULT_TEMPLATE = """
# {{ course.title }}

{% for section in sections %}
- {{ section.title }}

  {% if section.items %}
    {% for item in section['items'] %}

    - {{ item['title'] }}
    {{ item['description'] | replace('\n', '') }}

    {% endfor %}
  {% endif %}

{% endfor %}
"""
