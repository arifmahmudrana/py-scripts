"""
Main entry point for python -m course_content_extractor

This script extracts course content from a supported online platform
and generates a structured markdown file representing the course
curriculum using the provided course URL and curriculum API.
"""

import sys
import argparse
from .extractor import Extractor


def create_parser() -> argparse.ArgumentParser:
    """
    Create and return an argument parser for the CLI tool.

    Returns:
        argparse.ArgumentParser: Configured parser for command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="course_content_extractor",
        description="Extract course curriculum and generate markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m course_content_extractor "https://example-course.com/abc/" \\
      --curriculum-url "https://api.example.com/{course_id}/curriculum/" \\
      --title-strip " | Platform"
        """,
    )

    parser.add_argument(
        "course_url",
        help="Course URL to extract curriculum from (required).",
    )

    parser.add_argument(
        "-cu",
        "--curriculum-url",
        dest="curriculum_url",
        required=True,
        help=(
            "Curriculum API URL pattern with {course_id}"
            " placeholder (required).\n"
            "Example: https://api.example.com/{course_id}/curriculum/"
        ),
    )

    parser.add_argument(
        "-ts",
        "--title-strip",
        dest="title_strip",
        help="""
Optional string to strip from course title.
Example: ' | Platform'
        """,
    )

    return parser


def main() -> int:
    """
    Main function to execute course content extraction.

    Returns:
        int: Exit status code (0 for success, 1 for failure).
    """
    parser = create_parser()
    args = parser.parse_args()

    print("🚀 Course Content Extractor")
    print("=" * 50)

    try:
        extractor = Extractor(
            curriculum_url=args.curriculum_url,
            title_strip=args.title_strip,
        )
        extractor.extract_course_content(course_url=args.course_url)

    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        return 1

    except Exception as e:  # pylint: disable=broad-except
        print(f"\n❌ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
