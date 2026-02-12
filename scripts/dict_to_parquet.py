#!/usr/bin/env python3
"""Convert dict_fr_eng.txt (french english per line) to Parquet with columns french, english."""

import argparse
import sys
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert French–English dict txt to Parquet.")
    parser.add_argument(
        "input",
        nargs="?",
        default="dict_fr_eng.txt",
        help="Input text file (default: dict_fr_eng.txt)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default="dict_fr_eng.parquet",
        help="Output Parquet file (default: dict_fr_eng.parquet)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            french, english = parts[0], parts[1]
            rows.append({"french": french, "english": english})

    df = pd.DataFrame(rows, columns=["french", "english"])
    df.to_parquet(args.output, index=False, engine="pyarrow")
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
