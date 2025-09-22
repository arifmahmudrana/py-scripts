"""
Utility functions: configuration loader.
"""

from pathlib import Path
from typing import Any, Dict


import yaml


def load_config(path: str | Path) -> Dict[str, Any]:
    """
    Load YAML configuration file.

    Args:
        path: Path to YAML file.

    Returns:
        Parsed configuration dictionary.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
