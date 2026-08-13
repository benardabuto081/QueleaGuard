"""
QueleaGuard — Temporal Provenance Audit

Purpose:
    Trace observation_date from source occurrence/pseudo-absence records into
    the final modelling dataset. This is a readiness gate, not a modelling
    step. It is designed to detect silently reconstructed or mismatched dates.

Inputs:
    data/processed/occurrences_with_grid_cell.csv
    data/processed/pseudo_absences_final.csv
    data/processed/modelling_dataset_final.csv

Output:
    reports/temporal_provenance_audit.txt
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "temporal_provenance_audit.txt"


def normalise_date(series):
    return pd.to_datetime(series, errors="coerce").dt.strftime("%Y-%m-%d")


def main():
    occ = pd.read_csv(DATA / "occurrences_with_grid_cell.csv")
    pa = pd.read_csv(DATA / "pseudo_absences_final.csv")
    final = pd.read_csv(DATA / "modelling_dataset_final.csv")

    occ["source_date"] = normalise_date(occ.get("eventDate"))
    pa["source_date"] = normalise_date(pa.get("eventDate"))

    occ = occ.rename(columns={"key": "record_key"})
    pa = pa.rename(columns={"key": "record_key"})

    source = pd.concat([
        occ[["record_key", "source_date"]].assign(record_type="presence"),
        pa[["record_key", "source_date"]].assign(record_type="pseudo_absence"),
    ], ignore_index=True)

    final["final_date"] = normalise_date(final.get("observation_date"))
    final["record_type"] = final["record_type"].astype(str)

    audit = final[["record_key", "record_type", "final_date"]].merge(
        source, on=["record_key", "record_type"], how="left", validate="one_to_one"
    )

    audit["date_match"] = audit["final_date"].eq(audit["source_date"])
    audit["source_missing"] = audit["source_date"].isna()
    audit["final_missing"] = audit["final_date"].isna()
    audit["final_date_reconstructed_or_changed"] = (
        audit["source_date"].notna() & audit["final_date"].notna() & ~audit["date_match"]
    ) | (audit["source_missing"] & audit["final_date"].notna())

    lines = []
    lines.append("QUELEAGUARD — TEMPORAL PROVENANCE AUDIT")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Final rows audited: {len(audit)}")
    lines.append(f"Exact source→final date matches: {int(audit['date_match'].sum())}")
    lines.append(f"Source date missing: {int(audit['source_missing'].sum())}")
    lines.append(f"Final date missing: {int(audit['final_missing'].sum())}")
    lines.append(
        f"Potentially reconstructed/changed final dates: "
        f"{int(audit['final_date_reconstructed_or_changed'].sum())}"
    )
    lines.append("")

    lines.append("SOURCE DATE COMPLETENESS BY CLASS")
    lines.append("-" * 72)
    source_counts = source.groupby("record_type")["source_date"].apply(
        lambda s: f"{s.notna().sum()}/{len(s)} valid"
    )
    lines.extend(f"{idx}: {value}" for idx, value in source_counts.items())
    lines.append("")

    lines.append("POTENTIAL DATE PROVENANCE FAILURES")
    lines.append("-" * 72)
    failures = audit[audit["final_date_reconstructed_or_changed"]].copy()
    if failures.empty:
        lines.append("NONE")
    else:
        lines.append(failures[[
            "record_key", "record_type", "source_date", "final_date"
        ]].to_string(index=False))
    lines.append("")

    lines.append("FINAL DATE DISTRIBUTION BY CLASS")
    lines.append("-" * 72)
    temp = final.copy()
    temp["_date"] = pd.to_datetime(temp["observation_date"], errors="coerce")
    temp["_year"] = temp["_date"].dt.year
    temp["_month"] = temp["_date"].dt.month
    lines.append(temp.groupby(["record_type", "_year"]).size().to_string())
    lines.append("")
    lines.append(temp.groupby(["record_type", "_month"]).size().to_string())

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSaved: {REPORT}")

    if not failures.empty:
        raise SystemExit(
            "TEMPORAL PROVENANCE GATE: FAIL — inspect the report before modelling."
        )


if __name__ == "__main__":
    main()
