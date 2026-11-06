# CV Audit Protocol v1.2 (FROZEN)

Project: QueleaGuard. Subject: audit of the baseline logistic-regression spatial cross-validation (Log Entries 018-020).
Status: frozen by the project owner before any D, M0, R or M1 analysis was executed (see Log Entry 023). This file is an ASCII rendering of the approved text: mathematical symbols are spelled out and the content is unchanged. It is not edited in place; any change requires a new, logged version.

## 1. Purpose and status
- Purpose: to establish what the existing baseline analysis can and cannot support. It is not meant to improve scores or force a methodological conclusion.
- Entry 009: the original intent behind presence thinning is recorded as unresolved (Log Entry 021). No historical decision is rewritten and no dataset change is made.

## 2. Scope of inference (applies to every result below)
Coverage and design facts:
- All records lie within the ~50 km analysis extent around the Ahero scheme (Entry 002).
- Presences occupy 29 distinct coordinates in 20 grid cells. Two cells hold 87 of 133 presences (65.4%).
- Presences are opportunistic, presence-only GBIF/eBird observations, subject to the observer-effort and accessibility biases documented in Entries 004 and 009.
- Background points are other-species GBIF records (approximate target-group background, at most 5 per cell, 1:1 with presences, a single draw), so "absence" is never observed absence.
- Records span 2000-2026, and 145 of 266 fall in 2021-2024.
- The five folds are contiguous regions of this one landscape. No held-out region lies outside it.

What the results can support: descriptions of how the fitted model ranks the sampled presences against the sampled background in held-out sub-regions of this landscape and period, conditional on this background design.

What they cannot support:
- transfer to other schemes or regions;
- temporal forecasting or early-warning skill, because the folds share years;
- site-level generality, given about 20 occupied cells;
- absolute probability or prevalence;
- infestation or crop-damage claims;
- any claim that the evaluation is independent of the sampling process that produced both presences and background.

Spatial blocking reduces leakage between near neighbours across the train/test split. It does not remove dependence within folds, correct observer bias, or guarantee that fold boundaries exceed the (unmeasured) range of dependence. D2, D3 and R5 describe these properties and cannot establish that the design is adequate.

Weighting (V1, V2, cell-weighted metrics) changes how much each record contributes to a fitted objective or a metric. It does not correct sampling bias, remove spatial or temporal dependence, create independent information, or make any fit or metric an unbiased estimate. Weighted results only show sensitivity to a weighting choice and are not remedies.

## 3. Conventions

### 3.1 Analysis classes (kept separate in all reporting)
- D: data-only descriptive, with no model and no predictions.
- M0: baseline re-execution (model fitting, identical specification).
- R: evaluation-composition analyses that re-score fixed M0 predictions, with no refitting.
- M1: training-composition experiments in which models are refit.

### 3.2 Units
- A record is a row.
- A distinct coordinate is latitude/longitude rounded to 6 decimals (127 overall, 29 with presences, 103 with background; some coordinates host both classes).
- A presence-bearing cell is a grid_cell_id with at least one presence (20).
- A distinct (coordinate, date) vector is one row of baseline predictor values.

### 3.3 Distance and bands
- Distances are great-circle (haversine) kilometres.
- The predeclared bands are 0-1, 1-2, 2-5, 5-10, 10-20, 20-40, 40-80 and 80-120 km, with the lower bound inclusive and the upper bound exclusive.
- They are log-spaced for coverage and are not tied to any raster or ecological scale.

### 3.4 Banded Moran's I and the 30-pair threshold
Procedure:
- Weights: with n distinct points, values z_i and mean z_bar, w_ij = 1 if i != j and the distance falls in the band, else 0. S0_b = sum of w_ij = 2 P_b, where P_b is the number of unordered pairs in band b.
- Statistic: I_b = (n / S0_b) * sum_ij w_ij (z_i - z_bar)(z_j - z_bar) / sum_i (z_i - z_bar)^2.
- Reference value: E[I] = -1/(n-1) is printed for orientation only, with no variance, no p-values and no test.
- Standardisation: global (binary weights divided by S0_b), not row-standardised. Points with many in-band neighbours contribute proportionally more, so a tight cluster can dominate a band.
- Printed for every band: P_b, the number of participating points, and the largest share of the band's pairs involving any single point.
- Not estimable when P_b < 30, when sum_i (z_i - z_bar)^2 = 0, or when n < 3.

The 30-pair minimum is a predeclared operational threshold. It is not a statistical standard. It is not derived from a power calculation, a variance criterion or any published requirement for Moran's I, and no pair count guarantees a reliable estimate.
- Purpose: its only role is to keep statistics from very sparse bands from being over-read.
- When it was set: before any per-band pair counts were computed. Only the overall presence totals (406 pairs, 83 within-fold, 323 cross-fold), derivable from the fold table, were known.
- Why it is insufficient alone: pairs share points and are not independent, clustering lets a few points dominate a band, and distinct points are few.
- How it is handled: every band's counts are printed whether or not it passes, so a reader can apply any other threshold. The predeclared classification governs the report, and passing bands are labelled "computed under the predeclared rule", never "reliable".

### 3.5 Reporting rules
- Every table shows records alongside distinct coordinates, distinct dates and presence-bearing cells where relevant.
- No hypothesis tests, no required confidence intervals, no headline metric.
- Every predeclared result is reported, including null, adverse, inconclusive and "not estimable" results, with equal prominence.
- R and M1 findings are written up in separate sections.

### 3.6 Invariants and outputs
- The baseline, its results, modelling_dataset_final.csv, spatial_cv_folds.csv and all existing artefacts stay untouched.
- Write-once outputs (all analyses):
  - Every run writes to a new directory reports/cv_audit/<analysis-id>_<UTC timestamp>_<short HEAD>/, created with exist_ok=False. If the directory exists, the run stops.
  - Files are opened in exclusive-creation mode. No script truncates, overwrites, renames or deletes any existing file, and no --force option exists. Re-runs create a new directory.
  - Before writing, the run asserts that no output path resolves to an existing file or to reports/baseline_logistic_regression_cv_results.csv.
  - SHA-256 hashes of the protected inputs, the four baseline artefacts, and every existing file under reports/cv_audit/ are recorded before and after the run and must be identical, otherwise the run stops.
- Each run's manifest records HEAD commit, blob IDs of inputs and scripts, library versions, parameters, assertions and run time.
- All variants are diagnostic. No model or methodology is selected on score, and the Technical Architecture Section 9 metric designation is unchanged.
- Any adoption of thinning, weighting or grouped CV would be a separate logged decision with its own scientific justification, added beside the preserved baseline.
- Outputs are committed only after review.

## 4. Order of work
Gate 0, then D, then M0, then R, then M1. M0 waits for the baseline script to be committed so its manifest can record the blob ID.

## 5. D analyses (no model, no predictions)
- D1: site inventory. Fold x presence-bearing cell: records, distinct coordinates, distinct dates and year range, saved as an artefact. It also confirms the cell lists used in R and M1.
- D2: cross-fold distances.
  - For each held-out fold, class and unit (record, and distinct coordinate), report the distance to the nearest training record (any class) and, separately, the distance to the nearest training presence. Training is the other four folds.
  - Output: n, min, 5th/25th/50th/75th/95th percentile, max, and the full sorted vector.
  - Purely descriptive. No thresholds, no raster resolutions, and no classification of folds as independent or contaminated.
- D3: three statistics, kept separate.
  - D3a, predictor autocorrelation.
    - Unit: distinct coordinate, duplicates collapsed.
    - Strata: all (127), presence (29), background (103).
    - Variables: the static predictors elevation_m, slope_deg, dist_to_water_m, rice_pct_1000m, dist_to_nearest_rice_m, each asserted constant within a coordinate.
    - Dynamic predictors use the distinct (coordinate, date) vector as the unit, and w_ij additionally requires an identical date. Most bands are expected to be not estimable, and they are reported anyway.
    - It cannot support statements about unsampled areas, and dynamic predictors mix space and time.
  - D3b, presence site distribution (29 coordinates; 20 cells for context). It computes no Moran's I, and the two outputs are separate:
    - Nearest-neighbour distribution: one value per point (n = 29), giving min, quartiles, max, the sorted vector, and counts of same-fold versus other-fold neighbours.
    - Pairwise-distance distribution: all 406 unordered pairs counted per band, overall and split within-fold (83) and cross-fold (323). The pairs share points.
    - Limit: it reflects observation sites and observer effort, not ecological aggregation.
  - D3c, residual autocorrelation: defined in R5.
- D4: shared coarse covariates. Native CHIRPS and ERA5-Land cell indices are derived from coordinates. The grid definitions are taken from the extraction code (Entries 007 and 008) and recorded in the manifest. For each test record, count the training records sharing the cell, and sharing the cell plus date (identical values). Shared inputs are not proof of leakage.
- D5: temporal overlap. Month-by-year and season-by-year tables by fold. The folds share years, so no temporal claim follows.
- D6: predictor-space coverage.
  - Univariate (primary): per held-out fold, the share of test records outside the training min-max range for each of the ten numeric predictors.
  - Mahalanobis distance to the training-distribution centroid.
    - Vectors: the distinct training vectors are the distinct rows of the ten numeric predictors (exact equality of stored values) among the other four folds' records, both classes pooled. Test records enter none of the quantities below.
    - Standardisation and matrix: the centre mu and per-predictor SDs s_j (ddof = 1) come from the distinct training vectors. R is the sample correlation matrix of the same vectors (R = D^(-1/2) Sigma D^(-1/2), where Sigma is the sample covariance and D = diag(Sigma)). Predictors are used on their stored scales, with no transformation, so skewed predictors stay skewed and the diagnostic describes the sample as stored.
    - Distance: D^2 = z' R^(-1) z with z = (x - mu)/s, computed by solving a linear system rather than forming an explicit inverse. In exact arithmetic this equals the covariance form (x - mu)' Sigma^(-1) (x - mu). It is reported per test record and per distinct test vector.
  - Estimability checks (predeclared; applied per held-out fold in this order; the first failure makes that fold's Mahalanobis output "not estimable" and states the reason):
    1. Zero variance: a predictor is zero-variance if the distinct training vectors contain a single value for it (exact equality of stored values, so no floating-point tolerance is involved). The fold is not estimable and the predictor is named. The predictor is not dropped and no distance is computed on a reduced set, because a different dimension would change the quantity reported and make folds non-comparable. The univariate range check still covers it: any test value other than the constant counts as outside the training range.
    2. Count: fewer than 11 distinct training vectors (k + 1, with k = 10) is not estimable.
    3. Conditioning: kappa_2(R) = lambda_max/lambda_min from the eigenvalues of R (symmetric eigendecomposition). The fold is not estimable if lambda_min <= 0 or kappa_2(R) > 1e8.
  - Why R and why 1e8:
    - The raw covariance's condition number depends on measurement units (metres, millimetres, degrees, an index) rather than on collinearity, so it is not used. R is unit-free, and the distance is invariant to the rescaling.
    - 1e8 is a predeclared operational numerical-stability criterion, chosen as roughly 1/sqrt(eps) for double precision (eps ~ 2.2e-16, giving ~ 6.7e7, rounded up). Around that value about half of the 16 significant digits are lost in solving.
    - It is not a statistical standard and says nothing about how well Sigma is estimated. With roughly 120-190 distinct training vectors in 10 dimensions (derived from the established per-fold counts; exact figures are computed in D6), the estimate can be unstable at any condition number.
    - The threshold was fixed before any condition number was computed.
  - Always printed, for every fold whether or not it passes: the number of distinct training vectors, k, kappa_2(R) and the full eigenvalue vector, so a reader can apply another criterion.
  - Not done: no regularisation, no pseudo-inverse, no ridge and no dropped predictors.
  - Label and interpretation: the output is labelled "Mahalanobis distance to the training-distribution centroid". It describes position relative to the training centroid under the sample covariance. It is not a definitive measure of environmental extrapolation or novelty, and no threshold is used to declare a record extrapolated.
  - Out-of-range does not imply poor prediction.
- D7: background composition per fold. Records, cells, distinct coordinates and distinct vectors (background records 42/5/20/22/44; distinct (coordinate, date) 37/4/15/16/37). Fold presence rate is a sampling artefact of the 1:1 design and nearest-centroid assignment, and the background is a single draw.

## 6. M0: baseline re-execution (model fitting)
Purpose: persist per-record out-of-fold probabilities under the identical specification. It is a re-execution, not a new experiment. M0 runs as a new script that writes only to a new run directory under the 3.6 safeguard.

Dataset identity gates (all must pass before fitting). The row count alone does not identify the dataset, because two superseded versions exist (259 rows at commit 4728c6b; 266 rows x 20 columns at commit f83dc6d).
- HEAD commit is recorded.
- Hash comparisons: each gated file is hashed with the path-aware form git hash-object --path=<path> -- <path> (forward-slash repository paths) and compared with the recorded blob:
  - data/processed/modelling_dataset_final.csv against blob 60e1fd7654bc20322fdc2c00c32a2ef95d117a87 (last changed db7361b);
  - data/processed/spatial_cv_folds.csv against blob 67d8fec7c2b7aab6e98035cc8c916baf826338d0 (cdf2819);
  - data/processed/pseudo_absences_final.csv against blob 0b617c9f90d42c692c711a5d95a700cb585396ab (22151ff).
- Filter context: the path-aware form makes Git apply whatever clean filters its configuration and attributes define for that path. It does not guarantee any particular normalisation. The manifest therefore records core.autocrlf and git check-attr text eol -- <path> for each gated file. If a hash does not match, M0 stops, and no attempt is made to rewrite line endings to force a match.
- The dataset has 266 unique record_key values and exactly 29 columns, with these names in this order: record_key, grid_cell_id, observation_date, presence, record_type, within_scheme_boundary, latitude, longitude, month, day_of_year, season, rainfall_7d, rainfall_30d, rainfall_90d, temp_mean_7d, dewpoint_mean_7d, wind_mean_7d, temp_same_day, dewpoint_same_day, wind_same_day, ndvi_nearest_composite, ndvi_anomaly, rice_pct_500m, rice_pct_1000m, rice_pct_2000m, dist_to_nearest_rice_m, elevation_m, slope_deg, dist_to_water_m. It has 133/133 classes and no missing values.
- Its 133 background keys equal the key set of pseudo_absences_final.csv, and its 133 presence keys are all present in occurrences_with_grid_cell.csv.
- The fold file has one fold per record_key, the same key set as the dataset, IDs 0-4, and per-fold class counts (presence/background) of 8/42, 9/5, 11/20, 36/22, 69/44.
- No reconstruction: any mismatch stops M0. The dataset is never regenerated, rebuilt with assemble_final_dataset.py, or replaced with another version.

Season encoding (explicit, not inferred):
- The categories are fixed as ["dry_cool", "dry_hot", "long_rains", "short_rains"], and the run asserts the dataset's season values equal this set.
- The reference category is dry_cool, omitted by explicit construction rather than alphabetical drop_first.
- The dummy columns season_dry_hot, season_long_rains, season_short_rains are built by equality tests as 0/1 values, in that order.
- Assertions: rows with season == "dry_cool" have all three dummies 0, every other row has exactly its own dummy equal to 1, and the column names and order are exact.
- Cross-check: the result must equal pd.get_dummies(df["season"], prefix="season", drop_first=True) in values (cast to integer) and column order. This also documents that the original baseline's implicit reference was dry_cool.
- Category counts are recorded in the manifest, and any failure stops M0. The same construction and assertions apply in M1.

Preprocessing and features:
- Column order is the 10 numeric columns, then the three season dummies.
- The numeric columns are rice_pct_1000m, dist_to_nearest_rice_m, rainfall_30d, temp_mean_7d, dewpoint_mean_7d, wind_mean_7d, ndvi_nearest_composite, elevation_m, slope_deg, dist_to_water_m.
- StandardScaler is fit on training rows only, and the dummies are not scaled.
- There is no imputation, and the run asserts no missing values.

Model:
- LogisticRegression(max_iter=1000, random_state=42), with all other parameters at the installed version's defaults.
- get_params() and n_iter_ per fold are saved to the manifest, and any convergence warning is a failure.
- Library versions are recorded. The original run's versions were not recorded, so same-environment reproduction is assumed, not proven.

Metric definitions:
- The positive class is 1. Confusion matrices, precision, recall and F1 use predict with zero_division=0, and the matrix layout is [[TN, FP], [FN, TP]].
- ROC-AUC uses predict_proba[:,1].
- The aggregate is the unweighted mean with sample SD (ddof=1).
- Diagnostics use p_hat >= 0.5, and the run asserts no p_hat equals exactly 0.5.

Tolerances (predeclared choices; far above floating-point round-off, far below anything that could change a reported 3-decimal value):
- Against the original results file: n_test and n_presence_test exact. Precision, recall and F1 within 1e-12, and AUC within 1e-9.
- Confusion cells exact against the printed output and recomputed counts.
- The calibration and Fold 4 diagnostics exist only as printed 3-decimal values and are matched after rounding.
- Two runs in one session must agree on per-record probabilities within 1e-9.
- All of this assumes the results CSV is unmodified, which was established at Gate 0 (Log Entry 020).

Reference values (printed in the original run):

| Fold | n | Pres. | Precision | Recall | F1 | AUC | [[TN,FP],[FN,TP]] |
|---|---|---|---|---|---|---|---|
| 0 | 50 | 8 | 1.000 | 0.125 | 0.222 | 0.961 | [[42,0],[7,1]] |
| 1 | 14 | 9 | 0.700 | 0.778 | 0.737 | 0.867 | [[2,3],[2,7]] |
| 2 | 31 | 11 | 0.500 | 0.909 | 0.645 | 0.718 | [[10,10],[1,10]] |
| 3 | 58 | 36 | 0.882 | 0.833 | 0.857 | 0.886 | [[18,4],[6,30]] |
| 4 | 113 | 69 | 0.833 | 0.362 | 0.505 | 0.839 | [[39,5],[44,25]] |

- Aggregate, mean (SD): precision 0.783 (0.191), recall 0.602 (0.340), F1 0.593 (0.244), AUC 0.854 (0.089).
- Calibration diagnostic by fold (training presence rate / test presence rate / mean p_hat / fraction >= 0.5): 0: 0.579/0.160/0.053/0.020; 1: 0.492/0.643/0.750/0.714; 2: 0.519/0.355/0.517/0.645; 3: 0.466/0.621/0.539/0.586; 4: 0.418/0.611/0.341/0.265.
- Fold 4 groups (n; mean, median, min, max of p_hat; fraction >= 0.5):
  - Non-cell_0080 presences: 9; 0.508, 0.459, 0.304, 0.811; 0.444.
  - Non-cell_0080 background: 42; 0.164, 0.110, 0.003, 0.775; 0.095.
  - cell_0080 presences: 60; 0.431, 0.378, 0.144, 0.802; 0.350.
  - cell_0080 background: 2; 0.568, 0.568, 0.407, 0.729; 0.500.

Stop rule:
- Any failure halts the work.
- No change is made to code, data, folds, parameters or tolerances to obtain agreement.
- The investigation order is input identity, then environment and versions, then row order, then the provenance of the original run.
- The discrepancy is logged as a finding, and the original numbers keep the status "reported, provenance limited".

## 7. R analyses (evaluation composition; M0 predictions fixed, no refitting)
R1: per-site table, all folds. Per presence-bearing cell: records, coordinates, dates, p_hat (min, median, max) and fraction >= 0.5. Plus the background p_hat distribution by fold.

R2 and R3: decomposition template. For fold f with focal cell c, records are assigned by grid_cell_id alone, both classes included, with no sampling.

| Subset | Definition | Fold 4, c = cell_0080 | Fold 3, c = cell_0156 |
|---|---|---|---|
| All | all test records | 113 (69 presence / 44 background) | 58 (36 / 22) |
| Focal | records in c | 62 (60 / 2) | 27 (27 / 0) |
| Rest | records not in c | 51 (9 / 42): 2 presence cells, 5 coordinates | 31 (9 / 22): 5 presence cells, 5 coordinates |
| Cell-weighted | All, presence weight (N_pres/K)/n_cell, background weight 1 | K = 3, each presence cell totals 23 | K = 6, each presence cell totals 6 |

These counts are derived from the established fold table, and D1 verifies them.

Metric rules:
- Reported per subset: confusion matrix, recall, precision, F1, AUC, and mean p_hat and fraction >= 0.5 by class.
- Recall is defined when TP + FN > 0. Precision is defined when TP + FP > 0, otherwise it is reported as undefined, not 0. F1 is 2TP/(2TP + FP + FN), undefined when the denominator is 0.
- Subsets with fewer than 3 records in either class report counts, confusion matrix, recall, the p_hat distribution and the fraction >= 0.5 only. Fold 4's Focal subset (2 background records) and Fold 3's Focal subset (0 background) therefore get no AUC, precision or F1.
- AUC is roc_auc_score with scikit-learn's tie handling. The 3-record rule is a computability convention, and passing it does not make AUC informative.
- Every reported AUC is annotated with its presence-bearing cells and distinct coordinates, and flagged "<3 presence cells" when applicable (Fold 4 Rest: 2).
- Cell-weighted metrics use sample_weight. They re-describe the same predictions and do not create independent-site estimates (Section 2).

R4: leave-one-presence-cell-out re-scoring. For each fold and presence-bearing cell c:
- Primary (predeclared): evaluate the Rest subset, removing all evaluation records in c, presence and background. This treats the cell as the unit of dependence and is consistent with the Focal/Rest split and with V3.
- R4-alt: a separately labelled diagnostic that removes only c's presences and keeps its background records.
- Coincident cases: primary and alt coincide where a cell has no background in the fold (cell_0156) and are reported once. R2's Rest for cell_0080 and R3's Rest for cell_0156 are the R4-primary results for those cells and are also reported once.
- Output: each fold's metrics with the min-max across removed cells beside the full-fold values. This measures dependence on single sites and is not a confidence interval. Fold 1 has 2 presence cells and is flagged "single presence cell remaining".

R5: residual autocorrelation.
- Residual: r = y - p_hat, where p_hat is the M0 out-of-fold probability from the model that excluded the record's fold. Raw residuals are used because they are bounded. Their variance depends on p(1-p), and the sign is fixed by class.
- Strata: presence and background are never pooled. Within each class, within-fold pairs (which share one fitted model and its level shift) and cross-fold pairs (residuals from different models) are separate. That gives four strata and no pooled estimate.
- Unit and duplicates: distinct coordinate within class, mean residual per coordinate, and no zero-distance pairs.
- Statistic: banded Moran's I (3.4) with all printed diagnostics.
- Feasibility pre-check (counts only, before any statistic):
  - Presence has 29 coordinates (5, 2, 6, 9, 7 by fold), giving 406 pairs, 83 within-fold and 323 cross-fold, across 8 bands. Most bands are expected to be below 30, and Fold 1 has a single within-fold pair.
  - Background counts come from the same pre-check.
- Could support: descriptive statements about whether residuals at sampled locations are clustered, by stratum, in bands meeting the minimum.
- Cannot support:
  - an ecological autocorrelation range;
  - validation or invalidation of the fold design;
  - separation of misspecification from design effects, fold level shifts or unmodelled time effects;
  - statements about unsampled areas.
- If no band meets the minimum, the result is "not estimable under this design", and that is itself the finding.

## 8. M1 (training composition; models refit)

### 8.1 Common rules and test folds
- Predictors, model settings, the 0.5 threshold and the season construction (Section 6) are identical to the baseline. Test records are unweighted in every variant, as in the baseline, and weights apply only to training fits.
- V1 and V2 retain all five baseline test folds. For each fold, the training set is the other four folds with only the weights changed, and the fold's test records are unchanged.
- V3 and the reference ablations are evaluated only on folds that do not contain the manipulated cell. A fold "contains" the cell if any of its test records, presence or background, lies in the cell. For the fold that does contain it, no ablated fit is evaluated, because its baseline training set has no records of that cell (asserted by training-set digest equality with V0).
- Weights are passed as sample_weight.
- The scaler is fit unweighted on the training rows, as in the baseline. This is a deliberate isolation choice and also a limitation.
- Season dummy columns stay defined from the full dataset, and the run asserts none is constant in any training set.

### 8.2 Variants
| Variant | Definition |
|---|---|
| V0 | The baseline predictions from M0. |
| V1 | Exact-repeat weighting. Within a training set and class c with N_c records and G_c distinct (coordinate, date) groups, a record in a group of size m gets weight (N_c/G_c)/m. Class totals and the overall total are preserved. Evaluated on all five folds. |
| V2 | Cell-balanced presence weights: presence weight (N_pres/K)/n_cell, K being presence-bearing cells in the training set, background weight 1. It also upweights single-record cells, so it is a bracketing case, not a candidate model. Evaluated on all five folds. |
| V3 | Ablation of all records from the selected cell, including its background observations (62 for cell_0080: 60 presences, 2 background), with preprocessing refitted. It cannot be read as isolating presence clustering, because the class totals, class prior, N, scaler statistics and spatial and temporal coverage all change. |
| Reference ablations | The same as V3 for cell_0156, cell_0097, cell_0009 and cell_0099 (the other cells with at least 5 presences). |

Evaluated folds for the ablations (cell, presences/background in the cell, containing fold, folds evaluated):

| Cell | Presences / background | Containing fold | Folds evaluated |
|---|---|---|---|
| cell_0080 | 60 / 2 | 4 | 0, 1, 2, 3 |
| cell_0156 | 27 / 0 | 3 | 0, 1, 2, 4 |
| cell_0097 | 7 / 0 | 1 | 0, 2, 3, 4 |
| cell_0009 | 5 / 1 | 2 | 0, 1, 3, 4 |
| cell_0099 | 6 / 2 | 4 | 0, 1, 2, 3 |

### 8.3 V1 and V2: what the weighting does and does not do
- Observation weights: the only things that change by construction. The training rows, predictors, scaler inputs and model settings equal V0's.
- Distribution of statistical information: the weights redistribute the data-fit term across groups. How that affects information about the coefficients depends on the groups' feature vectors and fitted probabilities (sum_i s_i p_i (1 - p_i) x_i x_i'), so no claim is made from the weights alone.
  - Kish effective sample size, (sum s)^2 / sum(s^2) per class, is recorded as a descriptor of weight dispersion only.
  - No inference about regularisation or information is drawn from it.
- Penalised objective: scikit-learn documents the L2/lbfgs form as (1/2)||w||^2 + C * sum_i s_i l_i with the intercept unpenalised. The installed version's documentation is checked and recorded in the manifest.
  - The penalty term and C are unchanged and total data weight is preserved, so the nominal penalty-to-total-weight relation is unchanged.
  - The weighted data term is a different function, so the objective and its minimiser can differ from V0's. That follows from the different weights, not from the effective sample size.
  - Whether shrinkage changes is examined empirically through the recorded values per fit: ||beta_std||_2, weighted log-loss, penalty value, n_iter_ and convergence.
- Not preserved by class-total preservation: the baseline fitting problem, intercept or calibration, or scaler statistics (the unweighted scaler still counts duplicates at full multiplicity).
- Limit: weighting is not a correction for sampling bias or dependence (Section 2).

### 8.4 Per-fit recording
- Scaler mean_, scale_ and n_samples_seen_.
- A digest of the training record_key values.
- beta_std, the intercept, and the back-transformed original-scale values (beta_orig = beta_std/scale; b_orig = b - sum(beta_std * mean/scale); dummies unscaled).
- ||beta_std||_2, weighted log-loss and penalty value, n_iter_ and convergence status.

### 8.5 Coefficient interpretation
- V1 and V2: the training rows and scaler equal V0's, asserted by equality of mean_ and scale_. Coefficient differences are therefore attributable to the weights.
- V3 and the reference ablations: the scaler is refit, so comparisons use beta_orig and log-odds predictions, which are invariant to representation. beta_std differences alone are not interpreted.
- Residual confound: the L2 penalty acts on beta_std, so the effective penalty on a given original-scale model changes with the scaler, and the data change as well. The recorded results cannot separate the two. A fixed-scaler refit would be an extra model-fitting diagnostic and is not included unless separately approved.
- Reading changes: coefficient changes and sign flips are descriptive. With correlated predictors (Entry 019), 13 model columns and roughly 86 presence and 109 background distinct vectors, instability is expected and does not show that a predictor is unreliable. No coefficient-based selection or ranking is made.

### 8.6 Outputs
For each variant and evaluated fold:
- paired per-record change in p_hat (mean, mean absolute, 95th percentile, maximum), and the Spearman correlation with V0;
- change in standardised and original-scale coefficients, including sign flips;
- change in precision, recall, F1, AUC and mean p_hat, all reported with none designated headline;
- records, coordinates, dates and cells removed or reweighted.

Differences show the influence of training composition on fitted predictions. They are not evidence that a cell is biased, should be removed, or should be down-weighted, and the reference comparison (four cells) is descriptive. Results cannot select a model.
