"""Command line interface to tie together config -> core functions."""

import argparse
from .core import (
    load_yaml_config,
    extract_urls_from_file,
    filter_urls_by_domain,
    write_urls_to_file,
)


def run_from_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract URLs from text file and save filtered results."
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        default=None,
        help="Path to YAML config file with keys: input_text_file, output_file, domain_filter, unique_only",
    )
    parser.add_argument("--input", help="Direct input path (overrides config)")
    parser.add_argument("--output", help="Direct output path (overrides config)")
    parser.add_argument("--domain", help="Domain filter (overrides config)")
    parser.add_argument(
        "--unique", action="store_true", help="Force unique output (overrides config)"
    )

    args = parser.parse_args(argv)

    if not args.config and not args.input:
        parser.error("Either --config or --input must be provided.")

    if args.config:
        cfg = load_yaml_config(args.config)
    else:
        raise RuntimeError("Config required if not using --input (for now).")

    # CLI overrides
    if args.input:
        cfg["input_text_file"] = args.input
    if args.output:
        cfg["output_file"] = args.output
    if args.domain:
        cfg["domain_filter"] = args.domain
    if args.unique:
        cfg["unique_only"] = True

    # Main flow
    urls = extract_urls_from_file(cfg["input_text_file"])
    urls = filter_urls_by_domain(urls, cfg["domain_filter"])
    write_urls_to_file(urls, cfg["output_file"], unique=bool(cfg["unique_only"]))
    print(f"Processed {len(urls)} URLs (written to {cfg['output_file']}).")
