from __future__ import annotations

import argparse
from pathlib import Path

from data_processing import process_persona_predictions


DEFAULT_INPUT = "/mnt/data/round3_data_clean.xlsx"
DEFAULT_OUTPUT = "/mnt/data/round3_persona_predictions.csv"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Create row-level personas from Q20, Q19_1-4, Q28, Q29, Q30, and Q31, "
            "then ask each persona to answer the remaining survey questions."
        )
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input CSV or XLSX survey file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--limit", type=int, default=None, help="Optional row limit")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    print(f"Processing personas from {input_path} and saving to {output_path}...")
    process_persona_predictions(str(input_path), str(output_path), limit=args.limit)
