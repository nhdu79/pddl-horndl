#!/usr/bin/env python3
"""Summarize results.csv by grouping on (fragment, variant, task, tseitin)
and reporting count, mean, median, and geometric mean of total_time."""

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

_GROUP_KEYS = ("fragment", "variant", "task", "tseitin")
_OUT_FIELDS = ("fragment", "variant", "task", "tseitin", "count", "mean", "median", "geomean")


def geometric_mean(values: list[float]) -> float:
    return math.exp(sum(math.log(v) for v in values) / len(values))


def load(path: Path) -> dict[tuple, list[float]]:
    groups: dict[tuple, list[float]] = defaultdict(list)
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        missing = set(_GROUP_KEYS + ("total_time",)) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"results.csv is missing columns: {missing}")
        for row in reader:
            try:
                t = float(row["total_time"])
            except ValueError:
                continue
            key = tuple(row[k] for k in _GROUP_KEYS)
            groups[key].append(t)
    return groups


def summarize(groups: dict[tuple, list[float]]) -> list[dict]:
    rows = []
    for key in sorted(groups):
        values = groups[key]
        frag, variant, task, tseitin = key
        rows.append({
            "fragment": frag,
            "variant": variant,
            "task": task,
            "tseitin": tseitin,
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "geomean": geometric_mean(values),
        })
    return rows


def write(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=_OUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                **row,
                "mean":    f"{row['mean']:.6f}",
                "median":  f"{row['median']:.6f}",
                "geomean": f"{row['geomean']:.6f}",
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", nargs="?", default="results.csv",
        help="path to results.csv (default: results.csv)",
    )
    parser.add_argument(
        "-o", "--output", default="results_summary.csv",
        help="output file (default: results_summary.csv)",
    )
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)

    if not inp.exists():
        raise SystemExit(f"Input file not found: {inp}")

    groups = load(inp)
    if not groups:
        raise SystemExit("No data found in input file.")

    rows = summarize(groups)
    write(rows, out)

    print(f"Wrote {len(rows)} summary rows to {out}")
    print(f"  groups: {', '.join(f'{k[0]}/{k[1] or "ekab"}/{k[2]}/{k[3]}' for k in sorted(groups)[:5])}{'…' if len(groups) > 5 else ''}")


if __name__ == "__main__":
    main()
