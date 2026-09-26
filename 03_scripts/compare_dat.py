#!/usr/bin/env python3
"""Vergleicht eine CalculiX-.dat-Datei mit einer .dat.ref-Referenz.

Nutzung:
  python3 compare_dat.py job.dat job.dat.ref [--rtol 1e-4] [--atol 1e-6]
"""
from __future__ import annotations

import argparse
import math
import re
import sys

NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


def numbers(path: str) -> list[float]:
    vals: list[float] = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            for tok in NUM.findall(line):
                try:
                    vals.append(float(tok))
                except ValueError:
                    pass
    return vals


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("dat")
    p.add_argument("ref")
    p.add_argument("--rtol", type=float, default=1e-4)
    p.add_argument("--atol", type=float, default=1e-6)
    p.add_argument("--max-print", type=int, default=20)
    args = p.parse_args()

    a = numbers(args.dat)
    b = numbers(args.ref)
    n = min(len(a), len(b))
    diffs = []
    for i in range(n):
        if not math.isclose(a[i], b[i], rel_tol=args.rtol, abs_tol=args.atol):
            rel = abs(a[i] - b[i]) / max(abs(b[i]), 1e-30)
            diffs.append((i, a[i], b[i], rel))

    print(f"values: dat={len(a)}  ref={len(b)}  compared={n}")
    if len(a) != len(b):
        print("WARN: unterschiedliche Anzahl Zahlen")
    print(f"mismatches (rtol={args.rtol}, atol={args.atol}): {len(diffs)}")
    for i, av, bv, rel in diffs[: args.max_print]:
        print(f"  idx={i:6d}  dat={av: .8e}  ref={bv: .8e}  rel={rel:.3e}")
    if len(diffs) > args.max_print:
        print(f"  ... {len(diffs) - args.max_print} weitere")
    return 1 if diffs or len(a) != len(b) else 0


if __name__ == "__main__":
    sys.exit(main())
