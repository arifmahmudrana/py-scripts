"""CLI entry point for yaml_setter."""

import argparse
import sys
from pathlib import Path
from .yaml_setter import set_yaml_value


def main():
    parser = argparse.ArgumentParser(
        description="Set values in YAML files using dot notation paths"
    )
    parser.add_argument("input_file", help="Input file to read content from")
    parser.add_argument("yaml_file", help="Target YAML file path (e.g., a/b/c/d.yaml)")
    parser.add_argument(
        "yaml_path", help="YAML path using dot notation (e.g., a.b[8].c.d[3])"
    )

    args = parser.parse_args()

    # Read input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{args.input_file}' not found")
        return 1

    content = input_path.read_text(encoding="utf-8")

    # Set value in YAML
    try:
        set_yaml_value(args.yaml_file, args.yaml_path, content)
        print(f"✓ Successfully set value at '{args.yaml_path}' in '{args.yaml_file}'")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
