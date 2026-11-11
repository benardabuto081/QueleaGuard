from __future__ import annotations

import hashlib
import importlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

PROTOCOL_PATH = "docs/cv_audit_protocol_v1_2.md"
PROTOCOL_BLOB = "b569741912a4bc20465bdb031cf68de60bfe1494"
DATASET_PATH = "data/processed/modelling_dataset_final.csv"
FOLDS_PATH = "data/processed/spatial_cv_folds.csv"
PSEUDO_PATH = "data/processed/pseudo_absences_final.csv"
OCCURRENCES_PATH = "data/processed/occurrences_with_grid_cell.csv"

GATED_BLOBS = {
    DATASET_PATH: "60e1fd7654bc20322fdc2c00c32a2ef95d117a87",
    FOLDS_PATH: "67d8fec7c2b7aab6e98035cc8c916baf826338d0",
    PSEUDO_PATH: "0b617c9f90d42c692c711a5d95a700cb585396ab",
}
BASELINE_ARTEFACTS = [
    "src/train_baseline_logistic_regression.py",
    "src/diagnose_baseline_calibration.py",
    "src/diagnose_fold4_persistent_site.py",
    "reports/baseline_logistic_regression_cv_results.csv",
]
PROTECTED = [PROTOCOL_PATH, *GATED_BLOBS, *BASELINE_ARTEFACTS]

EXPECTED_COLUMNS = [
    "record_key", "grid_cell_id", "observation_date", "presence", "record_type",
    "within_scheme_boundary", "latitude", "longitude", "month", "day_of_year",
    "season", "rainfall_7d", "rainfall_30d", "rainfall_90d", "temp_mean_7d",
    "dewpoint_mean_7d", "wind_mean_7d", "temp_same_day", "dewpoint_same_day",
    "wind_same_day", "ndvi_nearest_composite", "ndvi_anomaly", "rice_pct_500m",
    "rice_pct_1000m", "rice_pct_2000m", "dist_to_nearest_rice_m", "elevation_m",
    "slope_deg", "dist_to_water_m",
]
STATIC_PREDICTORS = [
    "rice_pct_1000m", "dist_to_nearest_rice_m", "elevation_m", "slope_deg",
    "dist_to_water_m",
]
DYNAMIC_PREDICTORS = [
    "rainfall_30d", "temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d",
    "ndvi_nearest_composite",
]
NUMERIC_PREDICTORS = STATIC_PREDICTORS + DYNAMIC_PREDICTORS
EXPECTED_FOLD_COUNTS = {0: (8, 42), 1: (9, 5), 2: (11, 20), 3: (36, 22), 4: (69, 44)}

BANDS_KM = [(0, 1), (1, 2), (2, 5), (5, 10), (10, 20), (20, 40), (40, 80), (80, 120)]
MIN_PAIRS_PER_BAND = 30
KAPPA_LIMIT = 1e8
MIN_DISTINCT_VECTORS = 11
EARTH_RADIUS_KM = 6371.0088
LIBRARIES = ["numpy", "pandas", "scipy", "sklearn", "geopandas", "pyproj", "shapely", "rasterio", "netCDF4"]


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", check=check,
    )
    return result.stdout.strip()


def blob_hash(rel_path: str) -> str:
    return git("hash-object", f"--path={rel_path}", "--", rel_path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_entry(rel_path: str) -> dict[str, str]:
    entry = {"sha256": sha256_file(ROOT / rel_path)}
    if rel_path in PROTECTED:
        entry["blob"] = blob_hash(rel_path)
    return entry


def hash_state(keys: list[str] | None = None) -> dict[str, dict[str, str]]:
    if keys is None:
        audit_dir = ROOT / "reports" / "cv_audit"
        existing = [p.relative_to(ROOT).as_posix() for p in sorted(audit_dir.rglob("*")) if p.is_file()] if audit_dir.exists() else []
        keys = PROTECTED + existing
    return {key: hash_entry(key) for key in keys}


def library_versions() -> dict[str, str]:
    versions = {"python": sys.version.split()[0], "platform": platform.platform()}
    for name in LIBRARIES:
        try:
            versions[name] = getattr(importlib.import_module(name), "__version__", "unknown")
        except ImportError:
            versions[name] = "not installed"
    return versions


def haversine_km(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> np.ndarray:
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = phi2 - phi1
    delta_lambda = np.radians(lon2) - np.radians(lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def distance_matrix(lat: Any, lon: Any) -> np.ndarray:
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    return haversine_km(lat[:, None], lon[:, None], lat[None, :], lon[None, :])


def cross_distance_matrix(lat_a: Any, lon_a: Any, lat_b: Any, lon_b: Any) -> np.ndarray:
    lat_a, lon_a = np.asarray(lat_a, dtype=float), np.asarray(lon_a, dtype=float)
    lat_b, lon_b = np.asarray(lat_b, dtype=float), np.asarray(lon_b, dtype=float)
    return haversine_km(lat_a[:, None], lon_a[:, None], lat_b[None, :], lon_b[None, :])


def summarise(values: Any) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return {key: float("nan") for key in ["min", "p05", "p25", "p50", "p75", "p95", "max"]} | {"n": 0}
    q = np.percentile(array, [5, 25, 50, 75, 95], method="linear")
    return {"n": int(array.size), "min": float(array.min()), "p05": float(q[0]),
            "p25": float(q[1]), "p50": float(q[2]), "p75": float(q[3]),
            "p95": float(q[4]), "max": float(array.max())}


class Run:
    def __init__(self, analysis_id: str, scripts: list[str]) -> None:
        self.analysis_id = analysis_id
        self.scripts = scripts
        self.started = utc_now()
        self.head = git("rev-parse", "HEAD")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.before = hash_state()
        self.dir = ROOT / "reports" / "cv_audit" / f"{analysis_id}_{stamp}_{self.head[:7]}"
        self.dir.mkdir(parents=True, exist_ok=False)
        self.assertions: list[dict[str, Any]] = []
        self.parameters: dict[str, Any] = {}

    def _open(self, name: str):
        return open(self.dir / name, "x", encoding="utf-8", newline="")

    def write_text(self, name: str, text: str) -> None:
        with self._open(name) as handle:
            handle.write(text if text.endswith("\n") else text + "\n")

    def write_json(self, name: str, payload: Any) -> None:
        self.write_text(name, json.dumps(payload, indent=2, sort_keys=True, default=str))

    def write_csv(self, name: str, frame: pd.DataFrame) -> None:
        with self._open(name) as handle:
            frame.to_csv(handle, index=False, lineterminator="\n")

    def check(self, name: str, passed: bool, detail: str = "", fatal: bool = False) -> bool:
        self.assertions.append({"name": name, "passed": bool(passed), "detail": str(detail), "fatal": fatal})
        print(f"[{'PASS' if passed else 'FAIL'}] {name}" + (f" -- {detail}" if detail and not passed else ""))
        if fatal and not passed:
            self.stop(f"{name} failed. {detail}")
        return bool(passed)

    def stop(self, message: str) -> None:
        try:
            self.write_text("FAILED.txt", message)
        except FileExistsError:
            pass
        raise SystemExit(f"STOPPED: {message}")

    def finalize(self) -> bool:
        after = hash_state(list(self.before))
        changed = [key for key, value in self.before.items() if after.get(key) != value]
        self.check("protected_inputs_and_existing_audit_files_unchanged", not changed, ", ".join(changed))
        manifest = {
            "analysis_id": self.analysis_id, "started_utc": self.started, "finished_utc": utc_now(),
            "head": self.head, "git_status_short": git("status", "--short"),
            "script_blobs": {script: blob_hash(script) for script in self.scripts},
            "library_versions": library_versions(), "parameters": self.parameters,
            "hashes_before": self.before, "hashes_after": after, "assertions": self.assertions,
        }
        self.write_json("manifest.json", manifest)
        return not changed


def load_frame(run: Run) -> pd.DataFrame:
    for rel_path, expected in GATED_BLOBS.items():
        actual = blob_hash(rel_path)
        run.check(f"gated_blob:{rel_path}", actual == expected, actual, fatal=True)
    head_blob = git("rev-parse", f"HEAD:{PROTOCOL_PATH}")
    run.check("protocol_blob_at_HEAD", head_blob == PROTOCOL_BLOB, head_blob, fatal=True)
    work_blob = blob_hash(PROTOCOL_PATH)
    run.check("protocol_blob_in_working_copy", work_blob == PROTOCOL_BLOB, work_blob)

    frame = pd.read_csv(ROOT / DATASET_PATH)
    run.check("dataset_columns_exact_29", list(frame.columns) == EXPECTED_COLUMNS, str(list(frame.columns)), fatal=True)
    run.check("dataset_rows_266", len(frame) == 266, str(len(frame)), fatal=True)
    run.check("record_keys_unique", frame["record_key"].is_unique, fatal=True)
    counts = frame["presence"].value_counts().to_dict()
    run.check("classes_133_133", counts.get(1) == 133 and counts.get(0) == 133, str(counts), fatal=True)
    run.check("no_missing_cells", int(frame.isna().sum().sum()) == 0, fatal=True)

    folds = pd.read_csv(ROOT / FOLDS_PATH)
    run.check("fold_keys_match_dataset", set(folds["record_key"]) == set(frame["record_key"]) and folds["record_key"].is_unique, fatal=True)
    frame = frame.merge(folds, on="record_key", how="left", validate="one_to_one")
    per_fold = {int(f): (int(g["presence"].sum()), int((g["presence"] == 0).sum())) for f, g in frame.groupby("fold")}
    run.check("per_fold_class_counts", per_fold == EXPECTED_FOLD_COUNTS, str(per_fold), fatal=True)

    pseudo = pd.read_csv(ROOT / PSEUDO_PATH)
    background_keys = set(frame.loc[frame["presence"] == 0, "record_key"])
    run.check("background_keys_equal_pseudo_absences_final", background_keys == set(pseudo["key"]), fatal=True)
    occurrences = pd.read_csv(ROOT / OCCURRENCES_PATH)
    presence_keys = set(frame.loc[frame["presence"] == 1, "record_key"])
    run.check("presence_keys_in_occurrences", presence_keys <= set(occurrences["key"]), fatal=True)

    frame["coord"] = frame["latitude"].map("{:.6f}".format) + "," + frame["longitude"].map("{:.6f}".format)
    frame["coord_date"] = frame["coord"] + "|" + frame["observation_date"].astype(str)
    frame["year"] = frame["observation_date"].astype(str).str[:4].astype(int)
    return frame.reset_index(drop=True)
