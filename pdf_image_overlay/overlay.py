"""Core utilities for rendering a PDF page and overlaying an image.

This module exposes functions to:
- Load a YAML configuration
- Render a specific page of a PDF to a raster image
- Overlay another image onto that page image at (x, y)
- Save the composited image to an output path

Dependencies: PyMuPDF (fitz), Pillow (PIL), PyYAML
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Tuple

import fitz  # PyMuPDF
from PIL import Image
import yaml


@dataclass
class OverlayConfig:
    pdf_path: str
    overlay_image_path: str
    page_number: int  # 1-based index as provided in config
    x: int
    y: int
    output_image_path: str
    dpi: int = 150


def load_config(config_path: str) -> OverlayConfig:
    """Load OverlayConfig from a YAML file.

    Args:
        config_path: Path to YAML config file.

    Returns:
        OverlayConfig instance.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return OverlayConfig(
        pdf_path=data["pdf_path"],
        overlay_image_path=data["overlay_image_path"],
        page_number=int(data["page_number"]),
        x=int(data["x"]),
        y=int(data["y"]),
        output_image_path=data.get("output_image_path", "output.png"),
        dpi=int(data.get("dpi", 150)),
    )


def render_pdf_page_to_image(pdf_path: str, page_number_1_based: int, dpi: int = 150) -> Image.Image:
    """Render a specific PDF page to a PIL Image using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.
        page_number_1_based: Page number starting from 1.
        dpi: Desired render DPI (controls raster size). Default 150.

    Returns:
        PIL Image object (RGB).
    """
    if page_number_1_based < 1:
        raise ValueError("page_number must be 1 or greater")

    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)

    with fitz.open(pdf_path) as doc:
        if page_number_1_based > doc.page_count:
            raise IndexError(
                f"Requested page {page_number_1_based} exceeds total pages {doc.page_count}"
            )
        page = doc[page_number_1_based - 1]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        # Convert to PIL via PNG bytes to preserve correct stride
        png_bytes = pix.tobytes("png")
        img = Image.open(BytesIO(png_bytes))
        return img.convert("RGBA")


def overlay_image_on_base(base_image: Image.Image, overlay_path: str, position_xy: Tuple[int, int]) -> Image.Image:
    """Overlay an image onto a base image at the given (x, y) coordinates.

    Args:
        base_image: The base PIL Image (will be converted to RGBA).
        overlay_path: Path to the overlay image.
        position_xy: (x, y) coordinates where the top-left of overlay will be placed.

    Returns:
        Composited PIL Image in RGBA mode.
    """
    base_rgba = base_image.convert("RGBA")
    overlay_rgba = Image.open(overlay_path).convert("RGBA")

    x, y = position_xy
    canvas = Image.new("RGBA", base_rgba.size)
    canvas.paste(base_rgba, (0, 0))
    canvas.paste(overlay_rgba, (x, y), mask=overlay_rgba)
    return canvas


def process_overlay_from_config(config_path: str) -> str:
    """Process overlay based on config and save output.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Path to saved output image.
    """
    cfg = load_config(config_path)
    base_img = render_pdf_page_to_image(cfg.pdf_path, cfg.page_number, dpi=cfg.dpi)
    composited = overlay_image_on_base(base_img, cfg.overlay_image_path, (cfg.x, cfg.y))
    # Save as PNG to preserve transparency if present; use output extension as-is
    composited.save(cfg.output_image_path)
    return cfg.output_image_path


