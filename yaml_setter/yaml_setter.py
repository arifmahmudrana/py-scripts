"""Core YAML setter functionality."""

import re
from pathlib import Path
from typing import Any
import yaml


def parse_path(path: str) -> list:
    """Parse a.b[8].c.d[3][5] into [('a', None), ('b', 8), ('c', None), ('d', 3), (None, 5)]."""
    parts = []
    pattern = r"(\w+)|(\[(\d+)\])"

    for match in re.finditer(pattern, path):
        if match.group(1):  # It's a key
            key = match.group(1)
            parts.append((key, None))
        elif match.group(2):  # It's an index [N]
            index = int(match.group(3))
            # If last part has no index, add it there
            if parts and parts[-1][1] is None:
                parts[-1] = (parts[-1][0], index)
            else:
                # Consecutive index like [0][7]
                parts.append((None, index))

    return parts


def ensure_structure(data: dict, parts: list, value: Any) -> dict:
    """Create nested structure and set value."""
    current = data

    # Check first element - if it exists and needs to be replaced
    if parts and parts[0][0] is not None:
        first_key, first_index = parts[0]
        if first_key in data:
            if first_index is not None and not isinstance(data[first_key], list):
                data[first_key] = []
            elif (
                first_index is None
                and len(parts) > 1
                and not isinstance(data[first_key], dict)
            ):
                data[first_key] = {}

    for i, (key, index) in enumerate(parts[:-1]):
        # Handle consecutive indices (no key, just index)
        if key is None:
            # We're navigating deeper into a list
            if not isinstance(current, list):
                raise ValueError(f"Expected list at position {i}, got {type(current)}")

            while len(current) <= index:
                # Look ahead to determine what to create
                if i + 1 < len(parts):
                    next_key, next_index = parts[i + 1]
                    if next_key is None:  # Another index follows
                        current.append([])
                    elif next_index is not None:  # Key with index
                        current.append({})
                    else:  # Just a key
                        current.append({})
                else:
                    current.append(None)

            current = current[index]
            continue

        # Make sure current is a dict before accessing keys
        if not isinstance(current, dict):
            raise ValueError(
                f"Cannot access key '{key}' on non-dict type {type(current)}"
            )

        # Regular key handling
        if key not in current:
            # Look ahead to see if next item needs a list
            if i + 1 < len(parts):
                next_key, next_index = parts[i + 1]
                if index is not None:
                    current[key] = []
                elif next_key is None:  # Next is just an index
                    current[key] = []
                else:
                    current[key] = {}
            else:
                current[key] = [] if index is not None else {}

        # If key exists but is wrong type, replace it
        if index is None:
            if not isinstance(current[key], (dict, list)):
                # Look ahead
                if i + 1 < len(parts):
                    next_key, next_index = parts[i + 1]
                    current[key] = [] if next_key is None else {}
                else:
                    current[key] = {}
        elif not isinstance(current[key], list):
            current[key] = []

        # Handle list index
        if index is not None:
            # Extend list if needed
            while len(current[key]) <= index:
                # Check what the next item should be
                if i + 1 < len(parts):
                    next_key, next_index = parts[i + 1]
                    if next_key is None:  # Another index
                        current[key].append([])
                    elif next_index is not None:  # Key with index
                        current[key].append({})
                    else:  # Just a key
                        current[key].append({})
                else:
                    current[key].append({})

            # Check if item at index is the right type before navigating
            if i + 1 < len(parts):
                next_key, next_index = parts[i + 1]
                if next_key is None and not isinstance(current[key][index], list):
                    current[key][index] = []
                elif next_key is not None and not isinstance(current[key][index], dict):
                    current[key][index] = {}

            current = current[key][index]
        else:
            current = current[key]

    # Set the final value
    final_key, final_index = parts[-1]

    if final_key is None:
        # Final element is just an index [N]
        if not isinstance(current, list):
            raise ValueError(f"Expected list for final index, got {type(current)}")

        while len(current) <= final_index:
            current.append(None)

        current[final_index] = value
    elif final_index is not None:
        if final_key not in current:
            current[final_key] = []

        if not isinstance(current[final_key], list):
            current[final_key] = []

        while len(current[final_key]) <= final_index:
            current[final_key].append(None)

        current[final_key][final_index] = value
    else:
        current[final_key] = value

    return data


def set_yaml_value(yaml_file: str, yaml_path: str, value: Any) -> None:
    """Set a value in a YAML file at the specified path."""
    yaml_path_obj = Path(yaml_file)

    # Load existing YAML or create empty dict
    if yaml_path_obj.exists():
        with open(yaml_path_obj, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}
        # Create parent directories
        yaml_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Parse path and set value
    parts = parse_path(yaml_path)
    data = ensure_structure(data, parts, value)

    # Save YAML with nice formatting
    with open(yaml_path_obj, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
