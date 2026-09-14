from __future__ import annotations

import argparse
import sys

from ops_tool import load_config, run


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate daily operations CSV data and generate an exception report."
    )
    parser.add_argument("--input", help="Path to the input CSV. Overrides INPUT_CSV from .env.")
    parser.add_argument("--output", help="Directory for generated files. Overrides OUTPUT_DIR from .env.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.input, args.output)

    try:
        result = run(config.input_csv, config.output_dir, config.sla_hours)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("week10_ops_tool completed successfully")
    print(f"Records processed: {result['processed']}")
    print(f"Records needing attention: {result['failed']}")
    print(f"SLA breaches / overdue items: {result['sla_breaches']}")
    print(f"Validated data: {result['validated_path']}")
    print(f"Exceptions: {result['anomalies_path']}")
    print(f"Management report: {result['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
