"""
batch_merger.py

Batch file merging utility built on top of file_merger.merge_files_with_formatting.
Supports separate configurations for the first file and remaining files.
"""

import glob
from pathlib import Path
import yaml
from file_merger import merge_files_with_formatting


def merge_files_in_batches(config_path: str):
    """
    Merge files in batches based on a glob pattern and YAML configuration.

    Supports two merging strategies:
    1. first_file: Process the first matched file separately with its own config
    2. rest_files: Process remaining files in batches with chunk_size

    Parameters:
        config_path (str): Path to YAML configuration file.

    YAML Config Example:
        files: "a/*.txt"
        first_file:
          first_prepend: "---AT THE BEGINNING---\n"
          prefix: "---START---\n"
          join: "\n---NEXT FILE---\n"
          suffix: "\n---END---\n"
          final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"
          output_path: "b/c/"
          output_file_name: "abc.txt"
          size: 5
        rest_files:
          first_prepend: "---AT THE BEGINNING---\n"
          prefix: "---START---\n"
          join: "\n---NEXT FILE---\n"
          suffix: "\n---END---\n"
          final_append: "\n=== ALL FILES MERGED SUCCESSFULLY ===\n"
          output_path: "b/c/"
          output_file_name_pattern: "abc[batch].txt"
          chunk_size: 5
    """
    # Load configuration
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    files_pattern = config["files"]
    first_file_config = config.get("first_file", {})
    rest_files_config = config.get("rest_files", {})

    # Expand glob pattern and sort files
    all_files = sorted(glob.glob(files_pattern))
    if not all_files:
        print(f"⚠️ No files matched pattern: {files_pattern}")
        return

    print(f"📁 Found {len(all_files)} files matching pattern: {files_pattern}")

    # Process first file if config exists
    if first_file_config:
        first_file_size = first_file_config.get("size", 1)
        first_batch = all_files[:first_file_size]
        remaining_files = all_files[first_file_size:]

        # Extract first_file configuration
        output_path = Path(first_file_config.get("output_path", "output"))
        output_path.mkdir(parents=True, exist_ok=True)

        output_file = output_path / first_file_config.get(
            "output_file_name", "first_batch.txt"
        )

        print(f"📦 Processing first batch: {len(first_batch)} files → {output_file}")

        merge_files_with_formatting(
            *first_batch,
            first_prepend=first_file_config.get("first_prepend", ""),
            prefix=first_file_config.get("prefix", ""),
            join=first_file_config.get("join", "\n"),
            suffix=first_file_config.get("suffix", ""),
            final_append=first_file_config.get("final_append", ""),
            output_path=str(output_file),
        )
    else:
        remaining_files = all_files

    # Process remaining files if config exists
    if rest_files_config and remaining_files:
        chunk_size = rest_files_config.get("chunk_size", 10)
        output_path = Path(rest_files_config.get("output_path", "output"))
        output_path.mkdir(parents=True, exist_ok=True)

        output_file_name_pattern = rest_files_config.get(
            "output_file_name_pattern", "batch_[batch].txt"
        )

        # Process remaining files in chunks
        for batch_num, i in enumerate(
            range(0, len(remaining_files), chunk_size), start=1
        ):
            chunk = remaining_files[i : i + chunk_size]
            output_file = output_path / output_file_name_pattern.replace(
                "[batch]", str(batch_num)
            )

            print(
                f"📦 Processing rest batch {batch_num}: {len(chunk)} files → {output_file}"
            )

            merge_files_with_formatting(
                *chunk,
                first_prepend=rest_files_config.get("first_prepend", ""),
                prefix=rest_files_config.get("prefix", ""),
                join=rest_files_config.get("join", "\n"),
                suffix=rest_files_config.get("suffix", ""),
                final_append=rest_files_config.get("final_append", ""),
                output_path=str(output_file),
            )

    print(f"✅ Completed merging {len(all_files)} files")
