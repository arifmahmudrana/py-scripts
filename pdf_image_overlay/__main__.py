"""
Entry point for CLI usage of pdf_image_overlay.
"""

import argparse
import sys

from .overlay import process_overlay_from_config


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render a PDF page to an image and overlay another image at given coordinates, configured via YAML."
        )
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Path to YAML config file (pdf_path, overlay_image_path, page_number, x, y, output_image_path, dpi)",
    )

    args = parser.parse_args()

    output_path = process_overlay_from_config(args.config)
    print(f"Saved composited image to: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


