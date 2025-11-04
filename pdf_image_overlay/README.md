# 🖼️📄 pdf_image_overlay

Render a PDF page to an image and overlay another image at specified coordinates. Configuration is provided via a YAML file.

---

## 📂 Project Structure
```
pdf_image_overlay/
├── __init__.py
├── __main__.py
├── overlay.py
├── config.example.yaml
└── README.md
```

---

## ⚡ Usage

1. Create a `config.yaml` file:

```yaml
pdf_path: "./path/to/source.pdf"
overlay_image_path: "./path/to/overlay.png"
# 1-based page index
page_number: 1
# Top-left placement coordinates (in pixels on the rendered image)
x: 100
y: 150
output_image_path: "./output/composited_page1.png"
# Optional DPI for rendering the PDF page (affects image size)
dpi: 150
```

2. Run the tool:

```bash
python -m pdf_image_overlay -c ./pdf_image_overlay/config.yaml
```

This will:
- Render the specified PDF page to an image (controlled by `dpi`)
- Overlay the given image at `(x, y)` on the rendered page image
- Save the composited image to `output_image_path`

---

## 📦 Features

- Simple YAML configuration
- Renders PDF pages via PyMuPDF (no external system dependencies like poppler)
- Alpha-aware compositing with Pillow
- Usable as both a library and a CLI tool

---

## 🔧 Library API

```python
from pdf_image_overlay import (
    load_config,
    render_pdf_page_to_image,
    overlay_image_on_base,
    process_overlay_from_config,
)

# Load and process directly
output = process_overlay_from_config("./pdf_image_overlay/config.yaml")
print("Saved to:", output)
```

---

## ⚠️ Requirements

- Python 3.12.3 or higher
- PyYAML
- PyMuPDF (fitz)
- Pillow

See the main project README for environment setup.

