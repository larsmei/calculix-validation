#!/usr/bin/env python3
"""Laedt die ausgewaehlten offiziellen ccx-Testdateien von GitHub.

Quelle: https://github.com/Dhondtguido/CalculiX/tree/master/test
Ziel:   02_official_ccx_2.23/
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "02_official_ccx_2.23"
BASE = "https://raw.githubusercontent.com/Dhondtguido/CalculiX/master/test"

CASES = [
    "simplebeam", "oneel", "oneeltruss", "truss",
    "planestress", "planestrain", "planestress2",
    "beamd", "beamd2", "beamf", "beamf2",
    "beam8p", "beam8t", "beam8b", "beamabq", "beamabqnl", "beamb",
    "beamcom", "beamcontact", "beamcr", "beampd", "beampik",
    "achtel2", "achtelc", "axial", "axrad", "plate",
    "punch1", "punch2", "pret1", "pret2",
    "shellf", "shellnor", "solidshell1", "ball",
    "channel3", "pipe", "piperestrictor",
    "oneel8ra", "beamhtcr", "beamdy1",
]


def fetch(name: str, ext: str) -> bool:
    url = f"{BASE}/{name}{ext}"
    dest = DEST / f"{name}{ext}"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
    except Exception as exc:
        print(f"  skip {name}{ext}: {exc}")
        return False
    dest.write_bytes(data)
    print(f"  {name}{ext:8s}  {len(data):7d} B")
    return True


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"Quelle: {BASE}")
    print(f"Ziel:   {DEST}")
    n = 0
    for case in CASES:
        for ext in (".inp", ".dat.ref"):
            if fetch(case, ext):
                n += 1
    print(f"fertig: {n} Dateien")
    return 0 if n else 1


if __name__ == "__main__":
    sys.exit(main())
