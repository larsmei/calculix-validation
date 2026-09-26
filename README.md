# calculix-validation

Validierungssammlung für [CalculiX CrunchiX (ccx)](https://www.dhondt.de/):

- **`01_analytical/`** – selbstständige `.inp`-Decks mit geschlossener Lösung
- **`02_official_ccx_2.23/`** – ausgewählte offizielle Verification-Examples (ccx 2.23) inkl. `.dat.ref`
- **`03_scripts/`** – Vergleich und Laufsteuerung

Einheiten der analytischen Fälle: **mm, N, MPa, s, tonne, K**.
Stahl: E=210000, nu=0.3, rho=7.85e-9, alpha=1.2e-5.

## Voraussetzungen

- CalculiX-Solver `ccx` (2.2x-Linie), Pfad bekannt
- Python 3.8+

```bash
# Debian/Ubuntu
sudo apt install calculix-ccx
which ccx          # typisch /usr/bin/ccx

# oder Binary von https://www.dhondt.de/
```

```bash
git clone https://github.com/larsmei/calculix-validation.git
cd calculix-validation
```

## Testsuite ausführen

`--ccx` / `-c` ist **Pflicht**: Pfad zum Solver-Binary. Relativer Pfad, absoluter Pfad oder Name im `PATH` sind erlaubt. Das Skript prüft, ob die Datei existiert und ausführbar ist.

Gesamtlauf (analytisch + offiziell):

```bash
python3 03_scripts/run_suite.py --ccx /usr/bin/ccx
python3 03_scripts/run_suite.py -c ccx
```

Nur analytische Fälle (schnell, erster Check):

```bash
python3 03_scripts/run_suite.py --ccx /usr/bin/ccx --analytical
```

Nur offizielle `.inp` / `.dat.ref`-Paare:

```bash
python3 03_scripts/run_suite.py --ccx /usr/bin/ccx --official
```

Einzelnes Deck:

```bash
python3 03_scripts/run_suite.py --ccx /usr/bin/ccx --case 01_uniaxial_c3d8
python3 03_scripts/run_suite.py --ccx ./ccx --case simplebeam
```

Ohne `--ccx` bricht das Skript mit einer kurzen Anleitung ab.

| Flag | Bedeutung |
|------|-----------|
| `-c`, `--ccx PATH` | **Pflicht.** Pfad zum ccx-Solver |
| `--analytical` | nur analytische Decks |
| `--official` | nur offizielle Verification-Examples |
| `--case NAME` | einzelnes Deck (mehrfach möglich) |
| `--workdir DIR` | Arbeitsverzeichnis für `.dat`/`.frd` (Default: `work/`) |
| `--timeout SEC` | Timeout pro Job (Default: 120) |
| `--rtol`, `--atol` | Toleranzen für den `.dat.ref`-Vergleich |
| `-q` | knappe Ausgabe |

Exit-Code `0` wenn alle gewählten Fälle bestehen, sonst `1`.

`ccx` erwartet den Jobnamen ohne `.inp`. Der Runner kopiert die Decks nach `work/` und ruft `ccx JOB` auf.

Offizielle Beispiele werden beim ersten `--official`-Lauf automatisch von
https://github.com/Dhondtguido/CalculiX geholt, falls sie lokal fehlen:

```bash
python3 03_scripts/fetch_official.py
```

## Was geprüft wird

Analytische Sollwerte: `01_analytical/expected.json` und Kopfkommentar jeder `.inp`.

| Datei | Referenz |
|-------|----------|
| `01_uniaxial_c3d8.inp` | Sxx=100, Ux=4.7619047619e-3 |
| `02_uniaxial_c3d20r.inp` | wie 01 (Patch-Test) |
| `03_pure_shear_c3d8.inp` | Sxy=50, Ux=6.1904761905e-3 |
| `04_hydrostatic_c3d8.inp` | Sii=-100 |
| `05_cantilever_b32.inp` | Utip 0.19048 (Euler) … 0.19196 (Timoshenko) |
| `06_bar_tension_t3d2.inp` | U=1, S=210 |
| `07_thermal_bar_fixed.inp` | Sxx=-252, U=0 |
| `08_lame_cax8.inp` | St(a)=16.667, Ur(a)=4.540e-3 |
| `09_cantilever_frequency.inp` | f1=835.53 Hz |
| `10_ss_beam_b32.inp` | Umitte=0.047619 |
| `11_two_bar_truss.inp` | Uy=-0.133631, S=+-111.803 |
| `12_cantilever_c3d20r.inp` | Utip zwischen Euler und Timoshenko |

Patch-Tests (01–04, 06, 07, 11) müssen eng sitzen. Balken/Modal/3D: 2–5 %.

Offiziell: Vergleich `.dat` gegen `.dat.ref`.
Leere Referenzen gelten als bestanden, wenn ccx ohne Fehler endet.

## Lizenz

- Analytische Decks, Runner, Dokumentation: MIT (`LICENSE`)
- `02_official_ccx_2.23/`: CalculiX / GPL, Autor Guido Dhondt
