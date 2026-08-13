"""
QueleaGuard — Temporal Provenance Trace

Purpose:
    Investigate where observation_date values in the final modelling dataset
    came from when the immediate processed source files do not carry the same
    dates. This is diagnostic only: it never overwrites data or declares a
    reconstructed date authoritative.

Inputs:
    data/processed/occurrences_with_grid_cell.csv
    data/processed/pseudo_absences_final.csv
    data/processed/modelling_dataset_final.csv
    data/raw/gbif_kisumu_county_raw.csv
    data/raw/gbif_all_species_effort_pool.csv

Output:
    reports/temporal_provenance_trace.txt
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"
REPORT = ROOT / "reports" / "temporal_provenance_trace.txt"


def norm_date(value):
    if pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def candidate_dates(row):
    """Return date candidates from common GBIF Darwin Core fields."""
    out = {}
    for col in ["eventDate", "verbatimEventDate", "dateIdentified", "modified"]:
        if col in row.index:
            d = norm_date(row[col])
            if d:
                out[col] = d

    # GBIF/Darwin Core exports may retain year/month/day even when eventDate
    # is absent. Treat this only as a candidate reconstruction, never as
    # authoritative provenance.
    if "year" in row.index:
        try:
            year = int(float(row["year"]))
            month = int(float(row["month"])) if "month" in row.index and pd.notna(row["month"]) else None
            day = int(float(row["day"])) if "day" in row.index and pd.notna(row["day"]) else None
            if month and day:
                out["year+month+day (reconstructed)"] = f"{year:04d}-{month:02d}-{day:02d}"
            elif month:
                out["year+month (partial) "] = f"{year:04d}-{month:02d}"
            else:
                out["year (partial)"] = f"{year:04d}"
        except (TypeError, ValueError):
            pass
    return out


def key_series(df):
    for col in ["record_key", "key", "gbifID", "gbifid"]:
        if col in df.columns:
            return df[col].astype(str), col
    return None, None


def load(path):
    if not path.exists():
        return None
    return pd.read_csv(path, low_memory=False)


def main():
    final = load(PROCESSED / "modelling_dataset_final.csv")
    occ = load(PROCESSED / "occurrences_with_grid_cell.csv")
    pa = load(PROCESSED / "pseudo_absences_final.csv")
    raw_target = load(RAW / "gbif_kisumu_county_raw.csv")
    raw_effort = load(RAW / "gbif_all_species_effort_pool.csv")

    if final is None:
        raise SystemExit("Missing final modelling dataset.")

    lines = []
    lines += [
        "QUELEAGUARD — TEMPORAL PROVENANCE TRACE",
        "=" * 76,
        "",
        f"Final modelling rows: {len(final)}",
        "",
        "This report is diagnostic. A candidate date is NOT accepted as authoritative merely because it matches the final date.",
        "",
        "SOURCE FILE INVENTORY",
        "-" * 76,
    ]

    for label, df in [
        ("occurrences_with_grid_cell", occ),
        ("pseudo_absences_final", pa),
        ("gbif_kisumu_county_raw", raw_target),
        ("gbif_all_species_effort_pool", raw_effort),
        ("modelling_dataset_final", final),
    ]:
        if df is None:
            lines.append(f"{label}: MISSING")
        else:
            lines.append(f"{label}: {len(df)} rows x {len(df.columns)} columns")
            date_cols = [c for c in df.columns if any(token in c.lower() for token in ["date", "year", "month", "day"])]
            lines.append(f"  date-like columns: {date_cols}")

    final_key, final_key_name = key_series(final)
    final_date_col = "observation_date" if "observation_date" in final.columns else None
    if final_key is None or final_date_col is None:
        raise SystemExit("Final dataset lacks record key and/or observation_date.")

    final_work = final[[final_key_name, "record_type", final_date_col]].copy()
    final_work["record_key"] = final_work[final_key_name].astype(str)
    final_work["final_date"] = final_work[final_date_col].map(norm_date)

    lines += ["", "KEY-BASED SOURCE TRACE", "-" * 76]

    for label, df in [
        ("presence_processed", occ),
        ("pseudo_absence_processed", pa),
        ("raw_target", raw_target),
        ("raw_effort", raw_effort),
    ]:
        if df is None:
            continue
        keys, key_name = key_series(df)
        if keys is None:
            lines.append(f"{label}: no recognizable record-key column")
            continue

        source = df.copy()
        source["record_key"] = keys
        matched = final_work["record_key"].isin(set(source["record_key"]))
        lines.append(f"{label}: {int(matched.sum())}/{len(final_work)} final keys found in source")

        # Count exact matches against every recognizable date candidate.
        exact = 0
        any_candidate = 0
        examples = []
        source_index = {}
        for _, row in source.iterrows():
            source_index.setdefault(str(row["record_key"]), []).append(row)

        for _, frow in final_work.iterrows():
            rows = source_index.get(str(frow["record_key"]), [])
            if not rows or not frow["final_date"]:
                continue
            candidates = {}
            for row in rows:
                candidates.update(candidate_dates(row))
            if candidates:
                any_candidate += 1
            matches = [name for name, value in candidates.items() if value == frow["final_date"]]
            if matches:
                exact += 1
            elif candidates and len(examples) < 8:
                examples.append((frow["record_key"], frow["final_date"], candidates))

        lines.append(f"  final dates with at least one source-date candidate: {any_candidate}")
        lines.append(f"  exact final-date matches to a candidate: {exact}")
        if examples:
            lines.append("  non-matching examples:")
            for key, final_date, candidates in examples:
                lines.append(f"    {key}: final={final_date}; candidates={candidates}")

    lines += ["", "FINAL DATE SAMPLES", "-" * 76]
    sample = final_work.head(20)
    lines.append(sample[["record_key", "record_type", "final_date"]].to_string(index=False))

    lines += [
        "",
        "INTERPRETATION RULE",
        "-" * 76,
        "1. An exact match to a raw/source candidate is evidence of a possible provenance path, not proof of which pipeline created it.",
        "2. A date reconstructed from year/month/day is explicitly labelled reconstructed and must be traced to the generating script before acceptance.",
        "3. If final dates exist only in the final table and cannot be reproduced from retained source artifacts, modelling remains blocked.",
    ]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSaved: {REPORT}")


if __name__ == "__main__":
    main()
