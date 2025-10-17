"""
merger.py

Core logic for merging multiple files with configurable prefix, join, suffix,
and a final string appended after all files are merged.
"""

from pathlib import Path
from typing import List
import yaml


def merge_files_with_formatting(
    *files: List[str],
    first_prepend: str = "",
    prefix: str = "",
    join: str = "\n",
    suffix: str = "",
    final_append: str = "",
    output_path: str = "output.txt",
):
    """
    Merge multiple files into a single file with optional prefix, join string,
    suffix, and a final string appended after all files.

    Parameters:
        *files (str): Variable number of file paths to read from.
        first_prepend (str): String to prepended before any file's content.
        prefix (str): String to prepend before each file's content.
        join (str): String to insert between file contents.
        suffix (str): String to append after each file's content.
        final_append (str): String to append once after all files are merged.
        output_path (str): Path where the merged content will be stored.

    Returns:
        None
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as out:
        # Prepend the initial string if provided
        if first_prepend:
            out.write(first_prepend)
        for idx, file in enumerate(files):

            with open(file, "r", encoding="utf-8") as f:
                # Write prefix before file content
                out.write(prefix)
                # Stream file content line by line (efficient for large files)
                for line in f:
                    out.write(line)
                # Write suffix after file content
                out.write(suffix)

            # Add join string between files (but not after the last one)
            if idx < len(files) - 1:
                out.write(join)

        # Append final string once after all files are merged
        if final_append:
            out.write(final_append)

    print(f"✅ Merged {len(files)} files into {output_path}")


def load_config(config_path: str):
    """
    Load YAML configuration for first_prepend, prefix, join, suffix, final_append, and output_path.

    Parameters:
        config_path (str): Path to the YAML config file.

    Returns:
        dict: Configuration dictionary.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
