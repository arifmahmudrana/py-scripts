"""
Type definitions for course curriculum extraction.

This module defines the structured Pydantic models used throughout the extractor.
These models describe the shape of the curriculum API response and the context
used for generating markdown content via Jinja2 templates.
"""

from typing import List, Optional
from pydantic import BaseModel


class Item(BaseModel):
    """
    Represents a single item within a section.

    Attributes:
        title (str): Title of the item (e.g., lecture title).
        description (str): A brief description of the item content.
    """

    title: str
    description: str


class Section(BaseModel):
    """
    Represents a section of the course containing multiple items.

    Attributes:
        title (str): The title of the section.
        items (List[Item]): A list of course items within the section.
    """

    title: str
    items: List[Item]


class ApiResponse(BaseModel):
    """
    Top-level response model for the course curriculum API.

    This model nests the full structure returned by the API,
    particularly focusing on the curriculum data.
    """

    class CurriculumContext(BaseModel):
        """
        Represents the 'curriculum_context' object within the API response.

        Contains the actual curriculum data in the 'data' field.
        """

        class Data(BaseModel):
            """
            Represents the 'data' object inside 'curriculum_context'.

            Attributes:
                sections (List[Section]): A list of course sections with their items.
            """

            sections: List[Section]

        data: Data

    curriculum_context: CurriculumContext


class Context(BaseModel):
    """
    Represents the context object passed to the Jinja2 template
    for rendering the markdown output.

    Attributes:
        course (dict[str, Optional[str]]): Metadata about the course,
            such as title, normalized title, and course ID.
        sections (List[Section]): Structured course sections used in markdown generation.
    """

    course: dict[str, Optional[str]]
    sections: List[Section]
