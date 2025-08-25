"""
Type definitions for course curriculum extraction.

This module defines the structured types used throughout the extractor,
including course items, sections, curriculum data, and API responses.

These types are primarily used to annotate and validate data retrieved
from the course platform's API, as well as to structure the context
passed to the Jinja2 templates for markdown generation.
"""

from typing import List, Optional, TypedDict


class Item(TypedDict):
    """
    Represents an individual item in a section,
    such as a lesson, video, or resource.

    Attributes:
        description (str): A brief description of the item.
        title (str): The title of the item.
    """

    description: str
    title: str


class Section(TypedDict):
    """
    Represents a section in the course curriculum,
    which contains a list of items.

    Attributes:
        title (str): The title of the section.
        items (List[Item]): A list of items that belong to this
            section, such as lessons or videos.
    """

    title: str
    items: List[Item]


class CurriculumContextData(TypedDict):
    """
    Represents the structure of the curriculum context
    that contains all sections.

    Attributes:
        sections (List[Section]): A list of sections in the curriculum.
    """

    sections: List[Section]


class CurriculumContext(TypedDict):
    """
    Represents the main curriculum context,
    which holds the curriculum data.

    Attributes:
        data (CurriculumContextData): The curriculum data,
            including the sections.
    """

    data: CurriculumContextData


class ApiResponse(TypedDict):
    """
    Represents the structure of the API response
    containing the curriculum context.

    Attributes:
        curriculum_context (CurriculumContext): The curriculum context
            data retrieved from the API.
    """

    curriculum_context: CurriculumContext


class Context(TypedDict):
    """
    Represents the context passed to the template engine
    for rendering the course content.

    Attributes:
        course (dict[str, Optional[str]]): Information about the course,
            including its title and ID.
        sections (List[Section]): A list of sections within the
            course curriculum.
    """

    course: dict[str, Optional[str]]
    sections: List[Section]
