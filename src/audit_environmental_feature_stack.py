"""
QueleaGuard — Environmental Feature Stack Ground-Truth Audit
Milestone 4.5 -> Pre-Assembly

READ-ONLY:
- Does not modify datasets
- Does not modify scripts
- Does not submit/download anything
- Does not commit or change Git state

Purpose:
1. Identify the authoritative current PA dataset.
2. Audit all known environmental feature artifacts.
3. Verify 133-record accounting for PA features.
4. Check duplicate/missing record keys.
5. Check CHIRPS, ERA5, NDVI, elevation/slope, and distance-to-water coverage.
6. Compare current feature artifacts with the stale modelling dataset.
7. Report Git provenance for relevant files.
8. Produce a machine-readable audit report for the next assembly step.
"""

from pathlib import Path
import pandas as pd
import subprocess
import os
import json
from datetime import datetime

ROOT = Path(".")
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

REPORT_PATH = REPORT_DIR / "milestone_4_5_environmental_feature_audit.txt"

lines = []

def log(msg=""):
    print(msg)
    lines.append(str(msg))

def load_csv(label, path):
    path = Path(path)
    if not path.exists():
        log(f"[MISSING] {label}: {path}")
        return None

    try:
        df = pd.read_csv(path)
        log(f"[FOUND]   {label}: {path}")
        log(f"          rows={len(df):,}, columns={len(df.columns)}")
        return df
    except Exception as e:
        log(f"[ERROR]   {label}: {path}")
        log(f"          {type(e).__name__}: {e}")
        return None

def key_report(df, key_col, label):
    log(f"\n--- {label} KEY AUDIT ---")

    if df is None:
        log("SKIPPED: dataframe unavailable")
        return

    if key_col not in df.columns:
        log(f"[NO KEY] Column '{key_col}' not found.")
        log(f"Columns: {list(df.columns)}")
        return

    keys = df[key_col]

    log(f"Key column: {key_col}")
    log(f"Rows: {len(df):,}")
    log(f"Unique keys: {keys.nunique(dropna=True):,}")
    log(f"Null keys: {keys.isna().sum():,}")
    log(f"Duplicate rows by key: {keys.duplicated().sum():,}")

    dup = keys[keys.duplicated(keep=False)].dropna().unique()

    if len(dup):
        log(f"Duplicate key examples: {list(dup[:10])}")
    else:
        log("Duplicate keys: NONE")

def git_history(path):
    log(f"\n--- GIT HISTORY: {path} ---")

    result = subprocess.run(
        ["git", "log", "-5", "--format=%h | %ad | %s", "--date=iso", "--", str(path)],
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        log(result.stdout.rstrip())
    else:
        log("No Git history found.")

# ============================================================
# HEADER
# ============================================================

log("=" * 80)
log("QUELEAGUARD ENVIRONMENTAL FEATURE STACK — GROUND-TRUTH AUDIT")
log("=" * 80)
log(f"Audit timestamp: {datetime.now().isoformat()}")
log("READ-ONLY: NO FILES/DATASETS WILL BE MODIFIED")
log("")

# ============================================================
# 1. REPOSITORY STATUS
# ============================================================

log("=" * 80)
log("PART 1 — GIT WORKTREE STATE")
log("=" * 80)

result = subprocess.run(
    ["git", "status", "--short"],
    capture_output=True,
    text=True
)

if result.stdout.strip():
    log("Working-tree changes:")
    log(result.stdout.rstrip())
else:
    log("Working tree clean.")

result = subprocess.run(
    ["git", "branch", "--show-current"],
    capture_output=True,
    text=True
)

log(f"Current branch: {result.stdout.strip()}")

# ============================================================
# 2. AUTHORITATIVE PA DATASET
# ============================================================

log("")
log("=" * 80)
log("PART 2 — PSEUDO-ABSENCE DATASET")
log("=" * 80)

pa_candidates = [
    "data/processed/pseudo_absences_final.csv",
    "data/processed/pseudo_absences_final_v1_month_skewed.csv",
]

pa = None
pa_path = None

for candidate in pa_candidates:
    candidate_df = load_csv(
        "PA candidate",
        candidate
    )

    if candidate == "data/processed/pseudo_absences_final.csv":
        pa = candidate_df
        pa_path = candidate

if pa is None:
    log("\n[FATAL] Current pseudo_absences_final.csv is unavailable.")
else:
    log(f"\nCURRENT PA FILE: {pa_path}")
    log(f"CURRENT PA ROW COUNT: {len(pa)}")

    if len(pa) == 133:
        log("[PASS] Current PA dataset contains expected 133 records.")
    else:
        log(f"[FAIL] Expected 133 PA records, found {len(pa)}.")

    if "key" in pa.columns:
        key_report(pa, "key", "CURRENT PA")
    elif "record_key" in pa.columns:
        key_report(pa, "record_key", "CURRENT PA")
    else:
        log("[FAIL] No key/record_key column found in PA dataset.")

# ============================================================
# 3. ENVIRONMENTAL FILE DISCOVERY
# ============================================================

log("")
log("=" * 80)
log("PART 3 — ENVIRONMENTAL FEATURE FILE DISCOVERY")
log("=" * 80)

processed_dir = ROOT / "data" / "processed"
external_dir = ROOT / "data" / "external"

feature_files = []

for directory in [processed_dir, external_dir]:
    if directory.exists():
        for p in sorted(directory.glob("*.csv")):
            name = p.name.lower()

            if any(term in name for term in [
                "rain", "chirps",
                "era5", "meteor",
                "ndvi",
                "elevation", "slope",
                "hydro", "water",
                "distance",
                "environment",
                "feature"
            ]):
                feature_files.append(p)

if feature_files:
    for p in feature_files:
        try:
            df = pd.read_csv(p, nrows=5)
            full = pd.read_csv(p)

            log(f"\n{p}")
            log(f"  rows: {len(full):,}")
            log(f"  columns: {len(full.columns)}")
            log(f"  columns: {list(full.columns)}")
        except Exception as e:
            log(f"\n{p}")
            log(f"  [ERROR] {type(e).__name__}: {e}")
else:
    log("No obvious environmental feature CSVs discovered.")

# ============================================================
# 4. LOAD KNOWN FEATURE ARTIFACTS
# ============================================================

log("")
log("=" * 80)
log("PART 4 — KNOWN FEATURE ARTIFACTS")
log("=" * 80)

artifacts = {
    "NDVI PA v2": "data/processed/ndvi_features_pseudo_absence.csv",

    "ERA5 PA": "data/processed/meteorology_features_pseudo_absence.csv",

    "CHIRPS PA": "data/processed/rainfall_features_pseudo_absence.csv",

    "Modelling dataset":
        "data/processed/modelling_dataset_final.csv",

    "NDVI raw combined snapshot":
        "data/external/appeears_ndvi_combined_sources_snapshot.csv",

    "NDVI v2 raw 45-cell":
        "data/external/appeears_ndvi_pa_v2_gap_45cells.csv",

    "NDVI full history":
        "data/external/appeears_ndvi_full_history.csv",

    "NDVI old PA gap":
        "data/external/appeears_ndvi_pseudo_absence_gap.csv",
}

loaded = {}

for label, path in artifacts.items():
    loaded[label] = load_csv(label, path)

# ============================================================
# 5. NDVI AUDIT
# ============================================================

log("")
log("=" * 80)
log("PART 5 — NDVI PA FEATURE AUDIT")
log("=" * 80)

ndvi = loaded.get("NDVI PA v2")

if ndvi is not None:

    key_col = None

    for candidate in ["record_key", "key", "gbifID"]:
        if candidate in ndvi.columns:
            key_col = candidate
            break

    if key_col:
        key_report(ndvi, key_col, "NDVI PA FEATURES")

    log("\nNDVI columns:")
    log(str(list(ndvi.columns)))

    if "extraction_status" in ndvi.columns:
        log("\nExtraction status:")
        log(ndvi["extraction_status"].value_counts(dropna=False).to_string())

        success = (ndvi["extraction_status"] == "SUCCESS").sum()

        if success == 133:
            log("[PASS] NDVI SUCCESS count = 133")
        else:
            log(f"[FAIL] NDVI SUCCESS count = {success}")

    if "ndvi_nearest_composite" in ndvi.columns:
        vals = pd.to_numeric(
            ndvi["ndvi_nearest_composite"],
            errors="coerce"
        )

        log(
            f"\nNDVI value range: "
            f"{vals.min()} -> {vals.max()}"
        )

        log(f"NDVI null values: {vals.isna().sum()}")

        invalid = ((vals < -1) | (vals > 1)).sum()

        log(f"NDVI out-of-range values: {invalid}")

# ============================================================
# 6. ERA5 AUDIT
# ============================================================

log("")
log("=" * 80)
log("PART 6 — ERA5-LAND METEOROLOGY AUDIT")
log("=" * 80)

era5 = loaded.get("ERA5 PA")

if era5 is not None:

    log(f"ERA5 rows: {len(era5)}")

    for candidate in ["record_key", "key"]:
        if candidate in era5.columns:
            key_report(era5, candidate, "ERA5 PA")
            break

    log("\nERA5 columns:")
    log(str(list(era5.columns)))

# ============================================================
# 7. CHIRPS AUDIT
# ============================================================

log("")
log("=" * 80)
log("PART 7 — CHIRPS RAINFALL AUDIT")
log("=" * 80)

chirps = loaded.get("CHIRPS PA")

if chirps is None:
    log("[WARNING] Expected CHIRPS PA feature file was not found.")
else:

    log(f"CHIRPS rows: {len(chirps)}")

    for candidate in ["record_key", "key"]:
        if candidate in chirps.columns:
            key_report(chirps, candidate, "CHIRPS PA")
            break

    log("\nCHIRPS columns:")
    log(str(list(chirps.columns)))

# ============================================================
# 8. CROSS-FEATURE KEY RECONCILIATION
# ============================================================

log("")
log("=" * 80)
log("PART 8 — CROSS-FEATURE RECORD-KEY RECONCILIATION")
log("=" * 80)

def get_key_set(df):
    if df is None:
        return None

    for col in ["record_key", "key", "gbifID"]:
        if col in df.columns:
            return set(df[col].dropna().astype(str))

    return None

pa_keys = get_key_set(pa)
ndvi_keys = get_key_set(ndvi)
era5_keys = get_key_set(era5)
chirps_keys = get_key_set(chirps)

datasets = {
    "PA": pa_keys,
    "NDVI": ndvi_keys,
    "ERA5": era5_keys,
    "CHIRPS": chirps_keys,
}

for name, keys in datasets.items():
    if keys is None:
        log(f"{name}: NO USABLE KEY SET")
    else:
        log(f"{name}: {len(keys)} unique keys")

if pa_keys is not None:

    for name, keys in [
        ("NDVI", ndvi_keys),
        ("ERA5", era5_keys),
        ("CHIRPS", chirps_keys),
    ]:

        if keys is None:
            continue

        missing = pa_keys - keys
        extra = keys - pa_keys

        log(f"\nPA vs {name}")

        log(f"  PA keys missing from {name}: {len(missing)}")
        log(f"  {name} keys not present in PA: {len(extra)}")

        if missing:
            log(f"  Missing examples: {sorted(missing)[:10]}")

        if extra:
            log(f"  Extra examples: {sorted(extra)[:10]}")

# ============================================================
# 9. CURRENT MODELLING DATASET AUDIT
# ============================================================

log("")
log("=" * 80)
log("PART 9 — EXISTING MODELLING DATASET")
log("=" * 80)

model = loaded.get("Modelling dataset")

if model is not None:

    log(f"Rows: {len(model)}")
    log(f"Columns: {len(model.columns)}")

    if "presence" in model.columns:
        log("\nClass distribution:")
        log(model["presence"].value_counts(dropna=False).to_string())

    for candidate in ["record_key", "key"]:
        if candidate in model.columns:
            key_report(model, candidate, "MODELLING DATASET")
            break

    log("\nModelling dataset columns:")
    log(str(list(model.columns)))

# ============================================================
# 10. PA VS MODELLING DATASET PROVENANCE
# ============================================================

log("")
log("=" * 80)
log("PART 10 — PA PROVENANCE AGAINST EXISTING MODELLING DATASET")
log("=" * 80)

model_keys = get_key_set(model)

if pa_keys is not None and model_keys is not None:

    model_pa_keys = set()

    if "presence" in model.columns:
        for candidate in ["record_key", "key"]:
            if candidate in model.columns:
                model_pa_keys = set(
                    model.loc[model["presence"] == 0, candidate]
                    .dropna()
                    .astype(str)
                )
                break

    log(f"Current v2 PA keys: {len(pa_keys)}")
    log(f"Existing modelling-dataset PA keys: {len(model_pa_keys)}")

    log(
        f"Current v2 PA keys already in modelling dataset: "
        f"{len(pa_keys & model_pa_keys)}"
    )

    log(
        f"Current v2 PA keys NOT in modelling dataset: "
        f"{len(pa_keys - model_pa_keys)}"
    )

    log(
        f"Modelling PA keys not in current v2 PA set: "
        f"{len(model_pa_keys - pa_keys)}"
    )

# ============================================================
# 11. GIT PROVENANCE
# ============================================================

log("")
log("=" * 80)
log("PART 11 — GIT PROVENANCE")
log("=" * 80)

for path in [
    "data/processed/pseudo_absences_final.csv",
    "data/processed/meteorology_features_pseudo_absence.csv",
    "data/processed/rainfall_features_pseudo_absence.csv",
    "data/processed/ndvi_features_pseudo_absence.csv",
    "data/processed/modelling_dataset_final.csv",
]:
    git_history(path)

# ============================================================
# 12. FINAL DIAGNOSTIC SUMMARY
# ============================================================

log("")
log("=" * 80)
log("PART 12 — AUDIT SUMMARY")
log("=" * 80)

checks = []

if pa is not None:
    checks.append(
        ("Current PA count = 133", len(pa) == 133)
    )

if ndvi is not None:
    checks.append(
        ("NDVI rows = 133", len(ndvi) == 133)
    )

    if "extraction_status" in ndvi.columns:
        checks.append(
            (
                "NDVI SUCCESS = 133",
                (ndvi["extraction_status"] == "SUCCESS").sum() == 133
            )
        )

if era5 is not None:
    checks.append(
        ("ERA5 rows = 133", len(era5) == 133)
    )

if chirps is not None:
    checks.append(
        ("CHIRPS rows = 133", len(chirps) == 133)
    )

log("")

for label, passed in checks:
    log(f"{'PASS' if passed else 'FAIL'} — {label}")

log("")
log("IMPORTANT:")
log("This audit does NOT assemble or modify the modelling dataset.")
log("Any FAIL/WARNING must be resolved before final assembly.")
log("")

# ============================================================
# WRITE REPORT
# ============================================================

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("=" * 80)
print(f"Audit report saved to: {REPORT_PATH}")
print("=" * 80)

