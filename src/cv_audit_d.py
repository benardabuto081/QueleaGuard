from __future__ import annotations

import numpy as np
import pandas as pd

import cv_audit_common as cc

GRID_PATH = "data/processed/analysis_grid.geojson"
CHIRPS_CACHE_DIR = "data/external/chirps_cache"
UTM_CRS = "EPSG:32736"
WGS84_CRS = "EPSG:4326"
ERA5_RES = 0.1
ERA5_AREA = {"north": 1.0, "west": 34.2, "south": -1.0, "east": 35.6}
FOLDS = [0, 1, 2, 3, 4]
RAIN_COLUMNS = ["rainfall_7d", "rainfall_30d", "rainfall_90d"]
MET_COLUMNS = ["temp_mean_7d", "dewpoint_mean_7d", "wind_mean_7d", "temp_same_day", "dewpoint_same_day", "wind_same_day"]
FROZEN = {
    "presence_records": [8, 9, 11, 36, 69],
    "presence_coords": [5, 2, 6, 9, 7],
    "presence_cells": [4, 2, 5, 6, 3],
    "presence_vectors": [5, 6, 10, 24, 41],
    "background_records": [42, 5, 20, 22, 44],
    "background_vectors": [37, 4, 15, 16, 37],
}


def add_vector_id(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame["vector_id"] = frame.groupby(cc.NUMERIC_PREDICTORS, sort=False).ngroup()
    return frame


def inventory(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return frame.groupby(keys).agg(
        records=("record_key", "size"), cells=("grid_cell_id", "nunique"),
        coords=("coord", "nunique"), dates=("observation_date", "nunique"),
        coord_dates=("coord_date", "nunique"), vectors=("vector_id", "nunique"),
        year_min=("year", "min"), year_max=("year", "max"),
    ).reset_index()


def per_fold(table: pd.DataFrame, column: str) -> list[int]:
    return [int(table.loc[table["fold"] == f, column].sum()) for f in FOLDS]


def d1_site_inventory(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    presence = frame[frame["presence"] == 1]
    cells = sorted(presence["grid_cell_id"].unique())
    sub = frame[frame["grid_cell_id"].isin(cells)]
    base = inventory(sub, ["fold", "grid_cell_id"])
    pres = inventory(sub[sub["presence"] == 1], ["fold", "grid_cell_id"])
    pres = pres.rename(columns={"records": "presences", "coords": "presence_coords", "dates": "presence_dates",
                                "year_min": "presence_year_min", "year_max": "presence_year_max"})
    keep = ["fold", "grid_cell_id", "presences", "presence_coords", "presence_dates", "presence_year_min", "presence_year_max"]
    table = base.merge(pres[keep], on=["fold", "grid_cell_id"], how="left")
    table["background"] = table["records"] - table["presences"]
    run.write_csv("d1_site_inventory.csv", table)

    by_fold = inventory(presence, ["fold"])
    cells_by_fold = [int(presence.loc[presence["fold"] == f, "grid_cell_id"].nunique()) for f in FOLDS]
    run.check("D1_presence_records_per_fold", per_fold(by_fold, "records") == FROZEN["presence_records"], str(per_fold(by_fold, "records")))
    run.check("D1_presence_coordinates_per_fold", per_fold(by_fold, "coords") == FROZEN["presence_coords"], str(per_fold(by_fold, "coords")))
    run.check("D1_presence_cells_per_fold", cells_by_fold == FROZEN["presence_cells"], str(cells_by_fold))
    run.check("D1_presence_vectors_per_fold", per_fold(by_fold, "vectors") == FROZEN["presence_vectors"], str(per_fold(by_fold, "vectors")))
    totals = (len(presence), presence["coord"].nunique(), len(cells), presence["vector_id"].nunique())
    run.check("D1_presence_totals_133_29_20_86", totals == (133, 29, 20, 86), str(totals))
    top = table.set_index("grid_cell_id")
    c80, c156 = top.loc["cell_0080"], top.loc["cell_0156"]
    run.check("D1_cell_0080_60_presences_2_background_fold4", (c80["presences"], c80["background"], c80["fold"]) == (60, 2, 4), str(dict(c80)))
    run.check("D1_cell_0156_27_presences_0_background_fold3", (c156["presences"], c156["background"], c156["fold"]) == (27, 0, 3), str(dict(c156)))
    run.check("D1_two_cells_hold_87_presences", int(c80["presences"] + c156["presences"]) == 87)
    exact_repeats = len(presence) - presence["coord_date"].nunique()
    run.check("D1_47_presence_records_repeat_a_coordinate_and_date", exact_repeats == 47, str(exact_repeats))
    p80 = presence[presence["grid_cell_id"] == "cell_0080"]
    return [
        f"D1: {len(cells)} presence-bearing cells; cell_0080 presence dates={p80['observation_date'].nunique()}, "
        f"years {p80['year'].min()}-{p80['year'].max()}, presences in 2023-2024={int((p80['year'] >= 2023).sum())}; "
        f"exact repeated coordinate-date presence records={exact_repeats}."
    ]


def d2_cross_fold_distances(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    summary_rows, vector_rows = [], []
    for fold in FOLDS:
        train = frame[frame["fold"] != fold]
        references = {
            "nearest_training_record": train.drop_duplicates("coord"),
            "nearest_training_presence": train[train["presence"] == 1].drop_duplicates("coord"),
        }
        for presence in (1, 0):
            test = frame[(frame["fold"] == fold) & (frame["presence"] == presence)]
            units = {"record": test, "distinct_coordinate": test.drop_duplicates("coord")}
            for unit, points in units.items():
                for reference, ref in references.items():
                    matrix = cc.cross_distance_matrix(points["latitude"], points["longitude"], ref["latitude"], ref["longitude"])
                    distances = np.sort(matrix.min(axis=1))
                    summary_rows.append({"fold": fold, "presence": presence, "unit": unit, "reference": reference, **cc.summarise(distances)})
                    for rank, value in enumerate(distances, start=1):
                        vector_rows.append({"fold": fold, "presence": presence, "unit": unit, "reference": reference, "rank": rank, "distance_km": value})
    summary = pd.DataFrame(summary_rows)
    run.write_csv("d2_cross_fold_distance_summary.csv", summary)
    run.write_csv("d2_cross_fold_distance_vectors.csv", pd.DataFrame(vector_rows))
    lines = ["D2: nearest-training-record distance (km), record unit, presence class: fold n/min/median/max"]
    focus = summary[(summary["unit"] == "record") & (summary["presence"] == 1) & (summary["reference"] == "nearest_training_record")]
    for row in focus.itertuples():
        lines.append(f"  fold {row.fold}: n={row.n} min={row.min:.3f} p50={row.p50:.3f} max={row.max:.3f}")
    return lines


def banded_morans_i(values: np.ndarray, distance: np.ndarray, allowed: np.ndarray, same_cell: np.ndarray) -> list[dict]:
    n = len(values)
    z = values - values.mean()
    denominator = float((z ** 2).sum())
    rows = []
    for lower, upper in cc.BANDS_KM:
        mask = (distance >= lower) & (distance < upper) & allowed
        np.fill_diagonal(mask, False)
        degree = mask.sum(axis=1)
        pairs = int(degree.sum() // 2)
        reasons = []
        if pairs < cc.MIN_PAIRS_PER_BAND:
            reasons.append(f"fewer than {cc.MIN_PAIRS_PER_BAND} pairs")
        if denominator == 0:
            reasons.append("zero variance")
        if n < 3:
            reasons.append("n < 3")
        statistic = float("nan")
        if not reasons:
            statistic = float((n / (2 * pairs)) * (z @ mask.astype(float) @ z) / denominator)
        rows.append({
            "band_lo_km": lower, "band_hi_km": upper, "n_units": n, "pairs": pairs,
            "participating_points": int((degree > 0).sum()),
            "max_point_pair_share": float(degree.max() / pairs) if pairs else float("nan"),
            "pairs_same_cell": int((mask & same_cell).sum() // 2),
            "expected_I": -1.0 / (n - 1) if n > 1 else float("nan"),
            "morans_I": statistic,
            "status": "computed under the predeclared rule" if not reasons else "not estimable: " + "; ".join(reasons),
        })
    return rows


def d3a_predictor_autocorrelation(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    strata = {"all": frame, "presence": frame[frame["presence"] == 1], "background": frame[frame["presence"] == 0]}
    rows, violations = [], []
    for kind, predictors, unit_key in (("static", cc.STATIC_PREDICTORS, "coord"), ("dynamic", cc.DYNAMIC_PREDICTORS, "coord_date")):
        for stratum, records in strata.items():
            units = records.drop_duplicates(unit_key).reset_index(drop=True)
            distance = cc.distance_matrix(units["latitude"], units["longitude"])
            same_cell = (units["grid_cell_id"].to_numpy()[:, None] == units["grid_cell_id"].to_numpy()[None, :])
            if kind == "dynamic":
                allowed = units["observation_date"].to_numpy()[:, None] == units["observation_date"].to_numpy()[None, :]
            else:
                allowed = np.ones_like(same_cell, dtype=bool)
            for predictor in predictors:
                if (records.groupby(unit_key)[predictor].nunique() > 1).any():
                    violations.append(f"{kind}:{predictor}:{stratum}")
                for row in banded_morans_i(units[predictor].to_numpy(float), distance, allowed, same_cell):
                    rows.append({"kind": kind, "predictor": predictor, "stratum": stratum, "unit": unit_key, **row})
    table = pd.DataFrame(rows)
    run.write_csv("d3a_banded_morans_i.csv", table)
    run.check("D3a_predictors_constant_within_unit", not violations, ", ".join(violations))
    estimable = table[table["morans_I"].notna()]
    return [
        f"D3a: {len(table)} predictor x stratum x band rows; {len(estimable)} computed under the predeclared rule, "
        f"{len(table) - len(estimable)} not estimable (all rows are in d3a_banded_morans_i.csv)."
    ]


def d3b_presence_site_distribution(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    presence = frame[frame["presence"] == 1]
    fold_per_coord = presence.groupby("coord")["fold"].nunique()
    run.check("D3b_each_presence_coordinate_in_one_fold", bool((fold_per_coord == 1).all()))
    sites = presence.drop_duplicates("coord").reset_index(drop=True)
    n = len(sites)
    distance = cc.distance_matrix(sites["latitude"], sites["longitude"])
    folds = sites["fold"].to_numpy()
    masked = distance + np.diag(np.full(n, np.inf))
    nearest = masked.argmin(axis=1)
    nn = pd.DataFrame({
        "coord": sites["coord"], "grid_cell_id": sites["grid_cell_id"], "fold": folds,
        "nearest_neighbour_km": masked.min(axis=1), "neighbour_coord": sites["coord"].to_numpy()[nearest],
        "neighbour_fold": folds[nearest], "neighbour_same_fold": folds[nearest] == folds,
    })
    run.write_csv("d3b_nearest_neighbour_per_site.csv", nn)
    summary = {**cc.summarise(nn["nearest_neighbour_km"]), "same_fold_neighbours": int(nn["neighbour_same_fold"].sum()),
               "other_fold_neighbours": int((~nn["neighbour_same_fold"]).sum())}
    run.write_json("d3b_nearest_neighbour_summary.json", summary)
    run.write_csv("d3b_nearest_neighbour_sorted.csv", pd.DataFrame({"nearest_neighbour_km": np.sort(nn["nearest_neighbour_km"])}))
    i, j = np.triu_indices(n, k=1)
    pair_km, same_fold = distance[i, j], folds[i] == folds[j]
    edges = [(lower, upper) for lower, upper in cc.BANDS_KM] + [(cc.BANDS_KM[-1][1], np.inf)]
    rows = []
    for lower, upper in edges:
        in_band = (pair_km >= lower) & (pair_km < upper)
        rows.append({"band_lo_km": lower, "band_hi_km": upper, "pairs_all": int(in_band.sum()),
                     "pairs_within_fold": int((in_band & same_fold).sum()), "pairs_cross_fold": int((in_band & ~same_fold).sum())})
    run.write_csv("d3b_pairwise_band_counts.csv", pd.DataFrame(rows))
    run.check("D3b_pair_counts_406_83_323", (len(pair_km), int(same_fold.sum()), int((~same_fold).sum())) == (406, 83, 323),
              str((len(pair_km), int(same_fold.sum()), int((~same_fold).sum()))))
    return [
        f"D3b: {n} presence sites; nearest-neighbour km min={summary['min']:.3f} p50={summary['p50']:.3f} max={summary['max']:.3f}; "
        f"same-fold neighbours={summary['same_fold_neighbours']}, other-fold={summary['other_fold_neighbours']}."
    ]


def chirps_grid() -> dict:
    cache = cc.ROOT / CHIRPS_CACHE_DIR
    files = sorted(cache.glob("*.tif*")) if cache.exists() else []
    if files:
        try:
            import rasterio
            path = files[0]
            target = f"/vsigzip/{path.as_posix()}" if path.suffix == ".gz" else path.as_posix()
            with rasterio.open(target) as source:
                t = source.transform
            return {"origin_lon": t.c, "origin_lat": t.f, "pixel_w": t.a, "pixel_h": -t.e, "source": f"transform read from cached raster {path.name}"}
        except Exception as error:
            note = f"cached raster unreadable ({type(error).__name__}); "
    else:
        note = "no cached CHIRPS raster available; "
    return {"origin_lon": -180.0, "origin_lat": 50.0, "pixel_w": 0.05, "pixel_h": 0.05, "source": note + "documented CHIRPS global 0.05 degree grid, origin (-180, 50)"}


def analysis_cell_table(run: cc.Run, frame: pd.DataFrame) -> pd.DataFrame:
    import geopandas as gpd
    grid = gpd.read_file(cc.ROOT / GRID_PATH)
    centroids = gpd.GeoDataFrame({"grid_cell_id": grid["grid_cell_id"]}, geometry=grid.to_crs(UTM_CRS).geometry.centroid, crs=UTM_CRS).to_crs(WGS84_CRS)
    table = pd.DataFrame({"grid_cell_id": centroids["grid_cell_id"], "centroid_lat": centroids.geometry.y, "centroid_lon": centroids.geometry.x})
    table = table[table["grid_cell_id"].isin(frame["grid_cell_id"].unique())].reset_index(drop=True)
    run.check("D4_every_record_cell_found_in_analysis_grid", set(frame["grid_cell_id"]) <= set(table["grid_cell_id"]), fatal=True)
    chirps = chirps_grid()
    run.parameters["D4_chirps_grid"] = chirps
    run.parameters["D4_era5_grid"] = {"resolution_deg": ERA5_RES, "area": ERA5_AREA, "source": "documented 0.1 degree lattice, nearest point; extraction used xarray sel(method='nearest')"}
    col = np.floor((table["centroid_lon"] - chirps["origin_lon"]) / chirps["pixel_w"]).astype(int)
    row = np.floor((chirps["origin_lat"] - table["centroid_lat"]) / chirps["pixel_h"]).astype(int)
    table["chirps_pixel"] = "r" + row.astype(str) + "_c" + col.astype(str)
    lat_steps, lon_steps = table["centroid_lat"] / ERA5_RES, table["centroid_lon"] / ERA5_RES
    table["era5_point"] = "lat" + (np.rint(lat_steps) * ERA5_RES).round(1).astype(str) + "_lon" + (np.rint(lon_steps) * ERA5_RES).round(1).astype(str)
    near_ties = int((((lat_steps % 1) - 0.5).abs() < 1e-6).sum() + (((lon_steps % 1) - 0.5).abs() < 1e-6).sum())
    inside = bool(table["centroid_lat"].between(ERA5_AREA["south"], ERA5_AREA["north"]).all() and table["centroid_lon"].between(ERA5_AREA["west"], ERA5_AREA["east"]).all())
    run.check("D4_centroids_inside_era5_download_area", inside)
    run.check("D4_no_era5_nearest_point_ties", near_ties == 0, str(near_ties))
    run.write_csv("d4_analysis_cell_mapping.csv", table)
    return table


def shared_input_counts(frame: pd.DataFrame, unit_col: str, label: str) -> pd.DataFrame:
    parts = []
    for fold in FOLDS:
        test = frame[frame["fold"] == fold]
        train = frame[frame["fold"] != fold]
        by_unit = train[unit_col].value_counts()
        by_unit_date = train.groupby([unit_col, "observation_date"]).size()
        out = test[["record_key"]].copy()
        out[f"train_sharing_{label}"] = test[unit_col].map(by_unit).fillna(0).astype(int)
        out[f"train_sharing_{label}_same_date"] = [int(by_unit_date.get(key, 0)) for key in zip(test[unit_col], test["observation_date"])]
        parts.append(out)
    return pd.concat(parts)


def d4_shared_coarse_covariates(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    cells = analysis_cell_table(run, frame)
    frame = frame.merge(cells[["grid_cell_id", "chirps_pixel", "era5_point"]], on="grid_cell_id", how="left", validate="many_to_one")
    per_record = frame[["record_key", "fold", "presence", "observation_date", "grid_cell_id", "chirps_pixel", "era5_point"]].copy()
    for column, label in (("grid_cell_id", "analysis_cell"), ("chirps_pixel", "chirps_pixel"), ("era5_point", "era5_point")):
        per_record = per_record.merge(shared_input_counts(frame, column, label), on="record_key", validate="one_to_one")
    run.write_csv("d4_shared_inputs_per_test_record.csv", per_record)
    rows = []
    for (fold, presence), group in per_record.groupby(["fold", "presence"]):
        for label in ("analysis_cell", "chirps_pixel", "era5_point"):
            any_unit, same_date = group[f"train_sharing_{label}"], group[f"train_sharing_{label}_same_date"]
            rows.append({"fold": fold, "presence": presence, "unit": label, "test_records": len(group),
                         "share_with_training_record_in_unit": float((any_unit > 0).mean()),
                         "share_with_training_record_in_unit_same_date": float((same_date > 0).mean()),
                         "median_training_records_in_unit": float(any_unit.median()), "max_training_records_in_unit": int(any_unit.max()),
                         "max_training_records_in_unit_same_date": int(same_date.max())})
    run.write_csv("d4_shared_inputs_summary.csv", pd.DataFrame(rows))
    checks = []
    for unit, group_col, columns in (("analysis_cell", "grid_cell_id", RAIN_COLUMNS + MET_COLUMNS + cc.DYNAMIC_PREDICTORS),
                                     ("chirps_pixel", "chirps_pixel", RAIN_COLUMNS), ("era5_point", "era5_point", MET_COLUMNS)):
        groups = frame.groupby([group_col, "observation_date"])
        multi = groups.filter(lambda g: len(g) > 1)
        n_groups = multi.groupby([group_col, "observation_date"]).ngroups
        differing = int((multi.groupby([group_col, "observation_date"])[columns].nunique() > 1).any(axis=1).sum()) if n_groups else 0
        cross_cell = 0
        if unit != "analysis_cell" and n_groups:
            cross_cell = int((multi.groupby([group_col, "observation_date"])["grid_cell_id"].nunique() > 1).sum())
        checks.append({"unit": unit, "groups_with_multiple_records_same_date": n_groups, "groups_spanning_multiple_analysis_cells": cross_cell,
                       "groups_with_any_differing_value": differing, "columns_compared": ",".join(columns)})
    validation = pd.DataFrame(checks)
    run.write_csv("d4_mapping_validation.csv", validation)
    return [
        "D4: analysis-cell centroid used for dynamic extraction; mapping source for CHIRPS: " + run.parameters["D4_chirps_grid"]["source"] + ".",
        "D4 validation (groups sharing a unit and date; differing values flag a mapping or extraction discrepancy):",
        *[f"  {r.unit}: groups={r.groups_with_multiple_records_same_date}, spanning cells={r.groups_spanning_multiple_analysis_cells}, "
          f"groups with differing values={r.groups_with_any_differing_value}" for r in validation.itertuples()],
    ]


def d5_temporal_overlap(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    run.write_csv("d5_month_by_year_by_fold.csv", frame.groupby(["fold", "presence", "year", "month"]).size().rename("records").reset_index())
    run.write_csv("d5_season_by_year_by_fold.csv", frame.groupby(["fold", "presence", "year", "season"]).size().rename("records").reset_index())
    dates = frame.groupby("observation_date").agg(records=("record_key", "size"), n_folds=("fold", "nunique"),
                                                  folds=("fold", lambda s: ",".join(str(v) for v in sorted(set(s))))).reset_index()
    shared = dates[dates["n_folds"] > 1]
    run.write_csv("d5_dates_shared_across_folds.csv", shared)
    years = frame.groupby("fold")["year"].agg(["min", "max", "nunique"])
    return [f"D5: {len(dates)} distinct dates, {len(shared)} occur in more than one fold; years per fold: "
            + "; ".join(f"fold {f}={int(r['min'])}-{int(r['max'])}" for f, r in years.iterrows()) + "."]


def mahalanobis_fold(train_vectors: pd.DataFrame) -> tuple[dict, tuple | None]:
    k, n = train_vectors.shape[1], len(train_vectors)
    info = {"n_train_vectors": n, "k": k, "estimable": False, "reason": "", "kappa2_R": float("nan"),
            "lambda_min": float("nan"), "lambda_max": float("nan"), "eigenvalues": ""}
    constant = [c for c in train_vectors.columns if train_vectors[c].nunique() == 1]
    if constant:
        info["reason"] = "zero variance: " + ", ".join(constant)
        return info, None
    x = train_vectors.to_numpy(float)
    correlation = np.corrcoef(x, rowvar=False)
    eigenvalues = np.linalg.eigvalsh(correlation)
    info.update(lambda_min=float(eigenvalues[0]), lambda_max=float(eigenvalues[-1]), eigenvalues="; ".join(f"{v:.6g}" for v in eigenvalues))
    if eigenvalues[0] > 0:
        info["kappa2_R"] = float(eigenvalues[-1] / eigenvalues[0])
    if n < cc.MIN_DISTINCT_VECTORS:
        info["reason"] = f"fewer than {cc.MIN_DISTINCT_VECTORS} distinct training vectors"
    elif eigenvalues[0] <= 0:
        info["reason"] = "lambda_min <= 0"
    elif info["kappa2_R"] > cc.KAPPA_LIMIT:
        info["reason"] = f"kappa_2(R) > {cc.KAPPA_LIMIT:g}"
    if info["reason"]:
        return info, None
    info["estimable"] = True
    return info, (x.mean(axis=0), x.std(axis=0, ddof=1), correlation)


def d6_predictor_space(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    cols = cc.NUMERIC_PREDICTORS
    univariate, folds_out, records_out, vectors_out, lines = [], [], [], [], ["D6 Mahalanobis distance to the training-distribution centroid, by fold:"]
    for fold in FOLDS:
        train, test = frame[frame["fold"] != fold], frame[frame["fold"] == fold]
        test_vectors = test.drop_duplicates("vector_id")
        low, high = train[cols].min(), train[cols].max()
        outside_records = (test[cols] < low) | (test[cols] > high)
        outside_vectors = (test_vectors[cols] < low) | (test_vectors[cols] > high)
        for column in cols:
            univariate.append({"fold": fold, "predictor": column, "train_min": low[column], "train_max": high[column],
                               "test_records": len(test), "records_outside": int(outside_records[column].sum()),
                               "share_records_outside": float(outside_records[column].mean()),
                               "test_vectors": len(test_vectors), "vectors_outside": int(outside_vectors[column].sum()),
                               "share_vectors_outside": float(outside_vectors[column].mean())})
        any_rec, any_vec = outside_records.any(axis=1), outside_vectors.any(axis=1)
        univariate.append({"fold": fold, "predictor": "ANY_of_ten", "train_min": np.nan, "train_max": np.nan,
                           "test_records": len(test), "records_outside": int(any_rec.sum()), "share_records_outside": float(any_rec.mean()),
                           "test_vectors": len(test_vectors), "vectors_outside": int(any_vec.sum()), "share_vectors_outside": float(any_vec.mean())})
        info, model = mahalanobis_fold(train.drop_duplicates("vector_id")[cols])
        info["fold"] = fold
        if model is not None:
            mu, sd, correlation = model
            def distance(frame_part: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
                z = (frame_part[cols].to_numpy(float) - mu) / sd
                d2 = (z * np.linalg.solve(correlation, z.T).T).sum(axis=1)
                return d2, np.sqrt(np.maximum(d2, 0.0))
            d2_rec, d_rec = distance(test)
            records_out.append(pd.DataFrame({"fold": fold, "record_key": test["record_key"].to_numpy(), "presence": test["presence"].to_numpy(),
                                             "vector_id": test["vector_id"].to_numpy(), "d_squared": d2_rec, "distance": d_rec}))
            d2_vec, d_vec = distance(test_vectors)
            counts = test["vector_id"].value_counts()
            vectors_out.append(pd.DataFrame({"fold": fold, "vector_id": test_vectors["vector_id"].to_numpy(),
                                             "records": test_vectors["vector_id"].map(counts).to_numpy(), "d_squared": d2_vec, "distance": d_vec}))
            info.update({f"record_distance_{key}": value for key, value in cc.summarise(d_rec).items()})
        folds_out.append(info)
        status = "estimable" if info["estimable"] else "NOT ESTIMABLE (" + info["reason"] + ")"
        lines.append(f"  fold {fold}: distinct training vectors={info['n_train_vectors']}, k={info['k']}, kappa2(R)={info['kappa2_R']:.4g}, {status}")
    run.write_csv("d6_univariate_range.csv", pd.DataFrame(univariate))
    run.write_csv("d6_mahalanobis_fold_summary.csv", pd.DataFrame(folds_out))
    if records_out:
        run.write_csv("d6_mahalanobis_per_record.csv", pd.concat(records_out))
        run.write_csv("d6_mahalanobis_per_distinct_vector.csv", pd.concat(vectors_out))
    any_row = pd.DataFrame(univariate)
    any_row = any_row[any_row["predictor"] == "ANY_of_ten"]
    lines.append("D6 univariate: share of test records outside the training range on at least one predictor: "
                 + ", ".join(f"fold {r.fold}={r.share_records_outside:.3f}" for r in any_row.itertuples()))
    return lines


def d7_background_composition(run: cc.Run, frame: pd.DataFrame) -> list[str]:
    table = inventory(frame, ["fold", "presence"])
    run.write_csv("d7_composition_by_fold_and_class.csv", table)
    background = table[table["presence"] == 0]
    run.check("D7_background_records_per_fold", per_fold(background, "records") == FROZEN["background_records"], str(per_fold(background, "records")))
    run.check("D7_background_vectors_per_fold", per_fold(background, "vectors") == FROZEN["background_vectors"], str(per_fold(background, "vectors")))
    return [f"D7: background records per fold {per_fold(background, 'records')}, distinct vectors {per_fold(background, 'vectors')}, "
            f"distinct coordinates {per_fold(background, 'coords')}, cells {per_fold(background, 'cells')}."]


def main() -> None:
    run = cc.Run("D", ["src/cv_audit_common.py", "src/cv_audit_d.py"])
    run.parameters.update({"bands_km": cc.BANDS_KM, "min_pairs_per_band": cc.MIN_PAIRS_PER_BAND, "kappa_limit": cc.KAPPA_LIMIT,
                           "min_distinct_vectors": cc.MIN_DISTINCT_VECTORS, "earth_radius_km": cc.EARTH_RADIUS_KM, "numeric_predictors": cc.NUMERIC_PREDICTORS})
    frame = add_vector_id(cc.load_frame(run))
    lines = [f"CV audit D run {run.dir.name}", f"HEAD {run.head}", ""]
    for step in (d1_site_inventory, d2_cross_fold_distances, d3a_predictor_autocorrelation, d3b_presence_site_distribution,
                 d4_shared_coarse_covariates, d5_temporal_overlap, d6_predictor_space, d7_background_composition):
        lines.extend(step(run, frame))
        lines.append("")
    failed = [a["name"] for a in run.assertions if not a["passed"]]
    lines.append("Failed non-fatal checks: " + (", ".join(failed) if failed else "none"))
    run.write_text("run_summary.txt", "\n".join(lines))
    unchanged = run.finalize()
    print("\n".join(lines))
    print(f"\nOutput directory: {run.dir}")
    if not unchanged:
        raise SystemExit("STOPPED: protected inputs or existing audit files changed during the run")


if __name__ == "__main__":
    main()
