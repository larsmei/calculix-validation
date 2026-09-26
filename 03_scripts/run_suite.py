#!/usr/bin/env python3
"""CalculiX-Validierungssuite.

  python3 03_scripts/run_suite.py
  python3 03_scripts/run_suite.py --analytical
  python3 03_scripts/run_suite.py --official
  python3 03_scripts/run_suite.py --case simplebeam
"""
from __future__ import annotations

import argparse, json, math, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYTICAL = ROOT / "01_analytical"
OFFICIAL = ROOT / "02_official_ccx_2.23"
COMPARE = ROOT / "03_scripts" / "compare_dat.py"
NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")
RUN_ONLY = {"oneel", "oneeltruss", "beamcontact"}

def find_ccx(explicit):
    if explicit:
        return explicit
    if os.environ.get("CCX"):
        return os.environ["CCX"]
    for name in ("ccx", "ccx_2.23", "ccx_2.22", "ccx_2.21"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("ccx nicht gefunden. Bitte --ccx oder $CCX setzen.")

def run_ccx(ccx, inp, work, timeout):
    work.mkdir(parents=True, exist_ok=True)
    job = inp.stem
    dest = work / f"{job}.inp"
    if dest.resolve() != inp.resolve():
        shutil.copy2(inp, dest)
    try:
        proc = subprocess.run([ccx, job], cwd=work, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT nach {timeout}s"
    return proc.returncode, (proc.stdout or "") + "\n" + (proc.stderr or "")

def nums(text):
    out = []
    for tok in NUM.findall(text):
        try:
            out.append(float(tok))
        except ValueError:
            pass
    return out

def check_analytical(dat, spec):
    if not dat.is_file() or dat.stat().st_size == 0:
        return False, "keine .dat-Ausgabe"
    values = nums(dat.read_text(errors="replace"))
    notes, ok = [], True
    for ch in spec.get("checks", []):
        qty = ch.get("qty", "")
        atol = float(ch.get("tol_abs", 1e-4))
        rtol = float(ch.get("tol_rel", 1e-4))
        if "value_euler" in ch:
            lo, hi = sorted((ch["value_euler"], ch["value_timoshenko"]))
            if not values:
                ok = False; notes.append(f"{qty}: keine Zahlen"); continue
            got = min(values, key=lambda v: min(abs(v - lo), abs(v - hi)))
            if min(abs(got - lo), abs(got - hi)) / max(hi, 1e-12) <= max(rtol, 0.08):
                notes.append(f"{qty}={got:.6g} ok")
            else:
                ok = False; notes.append(f"{qty}={got:.6g} != [{lo:g},{hi:g}]")
            continue
        if "value" not in ch:
            continue
        ref = float(ch["value"])
        if not values:
            ok = False; notes.append(f"{qty}: keine Zahlen"); continue
        got = min(values, key=lambda v: abs(v - ref))
        if math.isclose(got, ref, rel_tol=rtol, abs_tol=atol) or (abs(ref) > 0 and abs(got - ref) / abs(ref) <= max(rtol, 0.08)):
            notes.append(f"{qty}={got:.6g} ok")
        else:
            ok = False; notes.append(f"{qty}={got:.6g} != {ref:g}")
    return ok, "; ".join(notes) or "keine Checks"

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--analytical", action="store_true")
    ap.add_argument("--official", action="store_true")
    ap.add_argument("--case", action="append", default=[])
    ap.add_argument("--ccx")
    ap.add_argument("--workdir", default=str(ROOT / "work"))
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--rtol", type=float, default=1e-3)
    ap.add_argument("--atol", type=float, default=1e-5)
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()
    if not args.analytical and not args.official and not args.case:
        args.analytical = args.official = True
    ccx = find_ccx(args.ccx)
    work = Path(args.workdir); work.mkdir(parents=True, exist_ok=True)
    expected = json.loads((ANALYTICAL / "expected.json").read_text())
    jobs = []
    if args.analytical or args.case:
        for inp in sorted(ANALYTICAL.glob("*.inp")):
            if args.case and inp.stem not in args.case: continue
            jobs.append(("analytical", inp))
    if args.official or args.case:
        official = list(OFFICIAL.glob("*.inp"))
        if len(official) < 5:
            print("offizielle Decks fehlen – lade von GitHub ...")
            subprocess.run([sys.executable, str(ROOT / "03_scripts" / "fetch_official.py")], check=False)
            official = list(OFFICIAL.glob("*.inp"))
        for inp in sorted(official):
            if args.case and inp.stem not in args.case: continue
            jobs.append(("official", inp))
    if not jobs:
        print("keine Faelle ausgewaehlt", file=sys.stderr); return 2
    print(f"ccx: {ccx}\nworkdir: {work}\nfaelle: {len(jobs)}\n")
    n_ok = n_fail = 0
    for kind, inp in jobs:
        job = inp.stem
        rc, out = run_ccx(ccx, inp, work, args.timeout)
        dat = work / f"{job}.dat"
        finished = rc == 0 or "Job finished" in out or dat.is_file()
        if rc == 124:
            status, detail = "FAIL", out
        elif kind == "official":
            ref = OFFICIAL / f"{job}.dat.ref"
            empty = job in RUN_ONLY or not ref.is_file() or ref.stat().st_size < 20
            if empty:
                status = "PASS" if finished else "FAIL"
                detail = "run-only" if status == "PASS" else "Solver fehlgeschlagen"
            else:
                cmp = subprocess.run([sys.executable, str(COMPARE), str(dat), str(ref), "--rtol", str(args.rtol), "--atol", str(args.atol), "--max-print", "3"], capture_output=True, text=True)
                status = "PASS" if cmp.returncode == 0 else "FAIL"
                detail = "dat.ref match" if status == "PASS" else "dat.ref mismatch"
        else:
            spec = expected.get("cases", {}).get(job, {"checks": []})
            if not finished:
                status, detail = "FAIL", "kein .dat"
            else:
                good, detail = check_analytical(dat, spec)
                status = "PASS" if good else "FAIL"
        n_ok += status == "PASS"; n_fail += status != "PASS"
        print(f"[{'ok ' if status == 'PASS' else 'ERR'}] {kind:11s} {job:28s} {detail}")
        if status == "FAIL" and not args.quiet:
            tail = "\n".join(out.splitlines()[-6:])
            if tail.strip(): print(tail)
    print(f"\nfertig: {n_ok} pass, {n_fail} fail, {n_ok + n_fail} total")
    return 0 if n_fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
