# Offizielle CalculiX-2.23-Verification-Examples

Diese Dateien stammen von Guido Dhondt und stehen unter der GPL.

Sie werden nicht alle fest im Git mitgefuehrt (grosse `.dat.ref`).
Stattdessen:

```bash
python3 03_scripts/fetch_official.py
```

Das legt `.inp` und `.dat.ref` aus
https://github.com/Dhondtguido/CalculiX/tree/master/test
hier ab.

`python3 03_scripts/run_suite.py --official` macht das automatisch, wenn der Ordner noch leer ist.
