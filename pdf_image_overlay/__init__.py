"""pdf_image_overlay package.

Utilities for rendering a PDF page to an image and overlaying another image
at specified coordinates, configured via YAML.
"""

from .overlay import (
    OverlayConfig,
    load_config,
    render_pdf_page_to_image,
    overlay_image_on_base,
    process_overlay_from_config,
)

__all__ = [
    "OverlayConfig",
    "load_config",
    "render_pdf_page_to_image",
    "overlay_image_on_base",
    "process_overlay_from_config",
]

