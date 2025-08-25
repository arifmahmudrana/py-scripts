#!/usr/bin/env python3
"""
Course Content Extractor

This module defines the Extractor class, which fetches course metadata
and curriculum structure from an online platform and generates a
structured markdown file.
"""

from typing import List, Optional, cast
from bs4 import BeautifulSoup, Tag
import requests
from jinja2 import Template

from .helpers import normalize_filename, DEFAULT_TEMPLATE
from .models import ApiResponse, Context, Section


class Extractor:
    """
    Handles extraction of course information and curriculum
    from a course platform.

    Attributes:
        curriculum_url (str): Template URL to fetch course curriculum data,
            with `{course_id}` placeholder.
        title_strip (Optional[str]): Optional suffix to remove from course title.
    """

    def __init__(self, curriculum_url: str, title_strip: Optional[str]):
        self.session = requests.Session()
        self.curriculum_url = curriculum_url
        self.title_strip = title_strip

    def extract_course_content(self, course_url: str):
        """
        Extract course metadata and curriculum, then write it to a markdown file.

        Args:
            course_url (str): URL of the course landing page.
        """
        course_info = self.extract_course_info(course_url)
        print(f"Extracted Course Title: {course_info['title']}")
        print(f"Extracted Course ID: {course_info['course_id']}")
        print(f"Normalized Title for Filename: {course_info['normalized_title']}")

        if not course_info["course_id"]:
            print("❌ Course ID not found.")
            return

        sections = self.fetch_curriculum(course_info["course_id"])
        if not sections:
            print("❌ No sections found in curriculum data.")
            return

        self.write_to_file(course_info, sections)

    def extract_course_info(self, course_url: str) -> dict[str, Optional[str]]:
        """
        Extract course title and course ID from the landing page HTML.

        Args:
            course_url (str): URL of the course landing page.

        Returns:
            dict[str, Optional[str]]: Dictionary with course title,
            normalized title, and course ID.
        """
        response = self.session.get(course_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find("title")
        course_title = title_tag.get_text().strip() if title_tag else None

        if (
            course_title is not None
            and self.title_strip is not None
            and self.title_strip in course_title
        ):
            course_title = course_title.replace(self.title_strip, "")

        normalized_title = normalize_filename(course_title) if course_title else None

        body_tag = soup.find("body")
        course_id = (
            cast(str, body_tag.get("data-clp-course-id"))
            if body_tag and isinstance(body_tag, Tag)
            else None
        )

        print("✅ Successfully extracted course info")
        return {
            "title": course_title,
            "normalized_title": normalized_title,
            "course_id": course_id,
        }

    def fetch_curriculum(self, course_id: str) -> List[Section]:
        """
        Fetch structured curriculum data from the platform's API.

        Args:
            course_id (str): Unique identifier of the course.

        Returns:
            List[Section]: List of course sections with their items.
        """
        print(f"📡 Fetching curriculum data for course ID: {course_id}")

        components = (
            "add_to_cart,available_coupons,base_purchase_section,buy_button,"
            "buy_for_team,cacheable_buy_button,cacheable_deal_badge,"
            "cacheable_discount_expiration,cacheable_price_text,"
            "cacheable_purchase_text,curated_for_ufb_notice_context,"
            "curriculum_context,deal_badge,discount_expiration,"
            "gift_this_course,incentives,instructor_links,"
            "lifetime_access_context,money_back_guarantee,price_text,"
            "purchase_tabs_context,purchase,recommendation,redeem_coupon,"
            "sidebar_container,purchase_body_container,one_click_checkout"
        )

        api_url = self.curriculum_url.format(course_id=course_id)
        response = self.session.get(
            api_url, params={"components": components}, timeout=30
        )
        response.raise_for_status()
        data: ApiResponse = response.json()

        return data.get("curriculum_context", {}).get("data", {}).get("sections", [])

    def write_to_file(
        self,
        course_info: dict[str, Optional[str]],
        sections: List[Section],
    ):
        """
        Render course content into a markdown file using a Jinja2 template.

        Args:
            course_info (dict): Metadata of the course (title, ID, normalized title).
            sections (List[Section]): List of course sections to be written.
        """
        template = Template(DEFAULT_TEMPLATE)
        context: Context = {"course": course_info, "sections": sections}
        markdown_content = template.render(context)

        output_filename = f"{course_info['normalized_title'] or 'course_content'}.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
