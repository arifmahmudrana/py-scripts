"""
batch_merger.py

Batch file merging utility built on top of file_merger.merge_files_with_formatting.
"""

import glob
from pathlib import Path
import yaml
from file_merger import merge_files_with_formatting


def merge_files_in_batches(config_path: str):
    """
    Merge files in batches based on a glob pattern and YAML configuration.

    Parameters:
        config_path (str): Path to YAML configuration file.

    YAML Config Example:
        files: "a/*.txt"
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
    prefix = config.get("prefix", "")
    join = config.get("join", "\n")
    suffix = config.get("suffix", "")
    final_append = config.get("final_append", "")
    output_path = Path(config.get("output_path", "output"))
    output_file_name_pattern = config.get(
        "output_file_name_pattern", "batch_[batch].txt"
    )
    chunk_size = int(config.get("chunk_size", 10))

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Expand glob pattern
    all_files = sorted(glob.glob(files_pattern))
    if not all_files:
        print(f"⚠️ No files matched pattern: {files_pattern}")
        return

    # Chunk files
    for batch_num, i in enumerate(range(0, len(all_files), chunk_size), start=1):
        chunk = all_files[i : i + chunk_size]
        output_file = output_path / output_file_name_pattern.replace(
            "[batch]", str(batch_num)
        )

        print(f"📦 Processing batch {batch_num}: {len(chunk)} files → {output_file}")

        merge_files_with_formatting(
            *chunk,
            prefix=prefix,
            join=join,
            suffix=suffix,
            final_append=final_append,
            output_path=str(output_file),
        )

    print(f"✅ Completed merging {len(all_files)} files into {output_path}")
