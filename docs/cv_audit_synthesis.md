# CV Audit Synthesis: What the Baseline Spatial Cross-Validation Can and Cannot Support

**Project:** QueleaGuard
**Version:** 1.0 (end of the audit phase)
**Document date:** 2026-11-17 (the Git commit timestamp is the verifiable record)
**Prepared by:** Project owner
**Subject:** the baseline logistic-regression spatial cross-validation (Log Entries 018-020)
**Protocol:** `docs/cv_audit_protocol_v1_2.md`, frozen, git blob b569741912a4bc20465bdb031cf68de60bfe1494 (Log Entry 023)

---

## 1. Purpose and status

The audit was designed to establish what the existing baseline evaluation can and cannot support. It was not meant to improve scores, select a model or force a methodological conclusion, and it did none of those. Every statement below carries an evidence status:

- **established:** computed from the committed data and code in an official, write-once run, with the run and entry cited;
- **hypothesis:** a candidate explanation that no audit analysis tested;
- **proposed:** an assumption or implementation choice that has not been verified against an external reference.

Nothing here replaces the log entries. Where a number appears, it is the number in the cited entry.

## 2. What was done

| Stage | Content | Scripts committed in | Outputs committed in | Log entry |
|---|---|---|---|---|
| Protocol | Pre-specification, frozen before any analysis; baseline artefacts committed first | 30e4379 (baseline artefacts) | 0ffa386 (protocol), d2a79d4 (Entries 020-023) | 020-023 |
| D | Data-only descriptive analyses D1-D7 (two byte-identical runs) | 05b7a93 | 1e18606 | 024 |
| M0 | Baseline re-execution with a reproduction gate | fcb5193 | 3805d04 | 025 |
| R | Evaluation composition with the M0 predictions fixed (R1-R5) | dcdb36d | cae5565 | 026 |
| M1 | Training composition: V1, V2, V3 and four reference ablations | a8cdc6e | b1dcf68 | 027 |

Every analysis wrote to a new write-once directory under `reports/cv_audit/` with a manifest that records the HEAD, the git blobs of the inputs and scripts, the library versions and the assertions; the protected inputs and all earlier audit files were hashed before and after each run and were unchanged. The baseline, its results, the dataset and the fold file were never modified.

## 3. Evidence ledger

| ID | Statement | Status | Source |
|---|---|---|---|
| L1 | The baseline numbers in Entry 020 are regenerated to floating-point precision (differences at most 1.1e-16) by the committed code and data; confusion matrices, aggregates, calibration table and Fold 4 groups match. | established | Entry 025 |
| L2 | Presences occupy 29 distinct coordinates in 20 grid cells. `cell_0080` (60 presences) and `cell_0156` (27) hold 87 of 133. 47 presence records repeat another record's coordinate and date. | established | Entry 024 (D1) |
| L3 | The folds hold 2 to 9 presence coordinates (5, 2, 6, 9, 7 for Folds 0-4); Fold 4's 69 presences sit at 7 coordinates. | established | Entry 024 (D1, D2) |
| L4 | Held-out presences lie 3.785 to 29.686 km from the nearest training record. No fold is classified as independent or contaminated. | established, descriptive | Entry 024 (D2) |
| L5 | The folds are spatial, not temporal: year ranges overlap almost completely, and 6 of 180 dates occur in more than one fold. | established | Entry 024 (D5) |
| L6 | Several static predictors are positively autocorrelated at 2-20 km. No dynamic predictor has a band with 30 same-date pairs, so none is estimable. | established, descriptive | Entry 024 (D3a) |
| L7 | Rainfall and meteorology are read at the analysis-cell centroid, so records in one cell share them on a date. No held-out presence shares a cell or CHIRPS pixel with a training record; identical same-date meteorology across folds exists for 2 of 133 presences. | established, conditional on the D4 grid mappings (proposed) | Entry 024 (D4) |
| L8 | The share of held-out records outside the training range on at least one predictor is 0.28, 0.50, 0.065, 0.28 and 0.062 for Folds 0-4. | established | Entry 024 (D6) |
| L9 | Fold 3's full-fold results depend on `cell_0156` (27 of 36 presences, all predicted positive): without it recall falls from 0.833 to 0.333 and ROC-AUC from 0.886 to 0.667. | established | Entry 026 (R3) |
| L10 | 39 of Fold 4's 44 false negatives are in `cell_0080` (recall 0.350 there), and recall in the remaining 9 presences is also low (0.444). | established | Entry 026 (R2) |
| L11 | Removing a single presence cell moves fold metrics little in Fold 2, moves recall and F1 over wide ranges in Folds 0, 1 and 3, and raises Fold 4's ROC-AUC above the full-fold value for each of its three cells. | established | Entry 026 (R4) |
| L12 | Within-fold presence residual autocorrelation is not estimable (at most 21 pairs per band); cross-fold presence residuals show none of note at 10-80 km; background residuals are positive at 5-40 km. Design effects cannot be separated from misspecification. | established, descriptive | Entry 026 (R5) |
| L13 | Fitted predictions depend unevenly on single training sites: removing `cell_0097` (7 records, one coordinate) drops Fold 3 recall from 0.833 to 0.028; removing `cell_0080` drops Fold 2 recall from 0.909 to 0.182; removing `cell_0009` (6 records) drops Fold 4 recall from 0.362 to 0.232; `cell_0156` and `cell_0099` have small effects. | established | Entry 027 (V3) |
| L14 | Exact-repeat weighting changes predictions modestly (mean absolute change at most 0.058) but moves Fold 4 recall from 0.362 to 0.522. | established | Entry 027 (V1) |
| L15 | Coefficient signs are unstable under weighting and ablation (for example ndvi_nearest_composite, negative in Folds 0-3 and positive in Fold 4 at baseline). This is descriptive and does not show a predictor is unreliable. | established, descriptive | Entry 027 |
| H1 | Fold 3's dependence on `cell_0097` reflects environmental or spatial similarity between `cell_0097` and `cell_0156`, with the rice-density coefficient as the carrier. | hypothesis | Entry 027 |
| H2 | Fold 4's thresholded metrics are sensitive to small probability shifts because many of its records lie near 0.5. | hypothesis | Entry 027 |
| H3 | The spatial fold design does not make the folds independent in the sense of training-composition influence (consistent with L6, L11, L13; no claim of leakage). | hypothesis | Entries 024, 026, 027 |
| P1 | The CHIRPS 0.05-degree grid (origin -180, 50) and the ERA5-Land 0.1-degree nearest-point mappings used in D4 are documented grids, not verified against the original extraction files. | proposed | Entry 024 |

## 4. What the evaluation can support

In the words of the protocol's scope section: descriptions of how the fitted model ranks the sampled presences against the sampled background in held-out sub-regions of this one landscape and period, conditional on this background design. In practice:

- the baseline logistic regression can be regenerated exactly, and its per-fold results are exact functions of the committed data and code (L1);
- each fold's result can be reported together with its composition (presence sites, cells and dominant cell) and with its sensitivity to single cells (L2, L3, L9-L11, L13);
- the five folds are five different small experiments with different composition, and each can be described as such.

## 5. What the evaluation cannot support

- **Transfer** to other schemes or regions: all folds lie within one landscape.
- **Temporal forecasting or early-warning skill:** the folds share years (L5).
- **Site-level generality:** about 20 occupied cells and 29 coordinates, with two cells holding 65 percent of the presences (L2, L3).
- **A cross-fold average as a summary of model quality:** the unweighted mean in Entry 020 combines folds that differ in composition and in dependence on single cells (L9-L11, L13). R and M1 compute no aggregate, deliberately.
- **Stability of thresholded metrics:** recall, precision and F1 at 0.5 change by large amounts under modest changes to the evaluation set or the training set (L9, L11, L13, L14).
- **Independence of the evaluation from the sampling process:** presences and background share the same spatial and observer structure, and the distances over which several predictors are autocorrelated (2-20 km) overlap the distances separating held-out presences from training records (3.8-29.7 km) (L4, L6, L12, H3).
- **Absolute probability or prevalence:** the background is a target-group draw and "absence" is never observed.
- **Infestation or crop-damage claims:** the target is recorded occurrence and habitat suitability, never infestation.
- **Any ranking of predictors or models** from coefficients or from the current fold metrics (L15).

Weighting (V1, V2, the cell-weighted metrics) is a sensitivity check and not a remedy: it does not correct sampling bias, remove dependence or create independent information.

## 6. Requirements for any later evaluation

These follow from the findings and are proposed for adoption by a logged decision; they do not change the frozen protocol or the baseline.

1. Report every fold result with its composition (presence records, coordinates, cells, dominant cell and share) and the fewer-than-3-presence-cell flag.
2. Report a Focal/Rest or leave-one-cell-out view beside any headline-style number, and never rely on an unweighted fold mean.
3. Treat exact repeats explicitly (a logged thinning or weighting variant), without altering the baseline.
4. Make a site-aware split (cell or coordinate groups) part of the evaluation design before comparing models, so the yardstick does not depend on one or two cells.
5. Keep the early-warning vocabulary out of results unless a temporal evaluation supports it.
6. Record library versions, input blobs and a manifest for every run, as the audit did.

## 7. Limitations of the audit

- The D4 grid mappings are proposed (P1); the D4 counts depend on them.
- The library versions of the original baseline run were never recorded. M0 shows that the committed code and data reproduce its numbers in two environments (scikit-learn 1.9.0 and 1.9.1) but not what the original environment was.
- The M1 script did not record V0's weighted log-loss, so V1 and V2 are compared with V0 on the coefficient norm and penalty only (Entry 027).
- Spearman correlations are sensitive in the third decimal to floating-point ties in 10 of the 30 M1 fits; they are read to two decimals (Entry 027).
- The audit examined one fold design (five presence-anchored k-means folds), one background draw and one model family. Replicate background draws, other fold sizes, a site-grouped design and temporal blocks were not run.
- The D stage was executed twice (byte-identical outputs, Entry 024); the reason for the second run is not recorded.
- The original intent behind presence thinning (Entry 009) remains unresolved (Entry 021); no thinning exists in the dataset.
- The scheme-boundary and rice-fraction questions (Entry 015), the 2023-2026 land-use check (Entry 017) and Level 2 items are untouched by the audit.
- The decision log has mixed line endings (CRLF and LF) under `core.autocrlf=true`, and run outputs are written with LF; cross-machine comparison of files should use git blob IDs and not file SHA-256 values.

## 8. How to reproduce

From a clean checkout at the commit that contains this file, with the pinned inputs: run `python src/cv_audit_d.py`, `python src/cv_audit_m0.py`, `python src/cv_audit_r.py` and `python src/cv_audit_m1.py` in that order. Each run creates a new directory under `reports/cv_audit/` and stops with `FAILED.txt` if an identity gate fails. The scripts that read earlier outputs (R and M1) are pinned to the committed M0 run directory by git blob ID.

---

> *Predict Early. Protect Harvests.* The audit's contribution to that aim is a clear statement of what these data and this evaluation can honestly say, and what they cannot.
