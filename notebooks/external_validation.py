"""
External validation for HeartGuard.

Compares the UCI Heart Failure Clinical Records cohort (299 patients,
Faisalabad, Pakistan) against a heart-failure cohort extracted from
MIMIC-IV (Beth Israel Deaconess, USA).

  A) Train on UCI (299)  -> test on MIMIC   [primary: does my model transfer?]
  B) Train on MIMIC      -> test on UCI     [supporting: does more data help?]

Usage:
    python notebooks/external_validation.py --mimic path/to/mimic_hf_cohort.csv

NOTE: the MIMIC CSV is credentialed data under a PhysioNet DUA.
Keep it OUT of version control. Only this script and aggregate results
should be committed.
"""

from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TARGET = "DEATH_EVENT"
RANDOM_STATE = 42

UCI_FEATURES = [
    "age", "anaemia", "creatinine_phosphokinase", "diabetes",
    "ejection_fraction", "high_blood_pressure", "platelets",
    "serum_creatinine", "serum_sodium", "sex", "smoking",
]

# ejection_fraction: ~0% structured coverage in MIMIC (4 / 31,369)
# creatinine_phosphokinase: ~60% missing (CK rarely ordered)
KNOWN_UNAVAILABLE = ["ejection_fraction", "creatinine_phosphokinase"]

EXPECTED_RANGES = {
    "age": (18, 120),
    "platelets": (10_000, 1_500_000),        # raw count per uL
    "serum_creatinine": (0.1, 20.0),         # mg/dL
    "serum_sodium": (100, 175),              # mEq/L
    "creatinine_phosphokinase": (5, 50_000), # U/L
    "ejection_fraction": (5, 90),            # percent
}

BINARY_COLUMNS = ["anaemia", "diabetes", "high_blood_pressure", "sex", "smoking"]


def make_pipeline() -> Pipeline:
    """Imputer sits INSIDE the pipeline so it is fit on training folds only."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=100, class_weight="balanced",
            max_depth=3, min_samples_leaf=15, random_state=RANDOM_STATE)),
    ])


def load_cohort(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        sys.exit(f"ERROR: {label} file not found: {path}")
    df = pd.read_csv(path)
    if TARGET not in df.columns:
        sys.exit(f"ERROR: {label} is missing the target column '{TARGET}'.")
    if "time" in df.columns:          # leakage; undefined at prediction time
        df = df.drop(columns=["time"])
    print(f"  {label:6s}: {len(df):>6,} rows, event rate {df[TARGET].mean():.3f}")
    return df


def resolve_shared_features(uci, mimic, keep_cpk: bool) -> list:
    excluded = [f for f in KNOWN_UNAVAILABLE
                if not (keep_cpk and f == "creatinine_phosphokinase")]
    shared, dropped = [], {}
    for feat in UCI_FEATURES:
        if feat in excluded:
            dropped[feat] = "known-unavailable in MIMIC"
        elif feat not in mimic.columns:
            dropped[feat] = "absent from MIMIC CSV"
        elif mimic[feat].isna().all():
            dropped[feat] = "100% missing in MIMIC"
        else:
            shared.append(feat)
    print("\nFeature alignment")
    print(f"  shared ({len(shared)}): {', '.join(shared)}")
    for feat, reason in dropped.items():
        print(f"  dropped: {feat} -- {reason}")
    if len(shared) < 3:
        sys.exit("\nERROR: fewer than 3 shared features. Check the MIMIC schema.")
    return shared


def check_units(uci, mimic, features) -> None:
    """Tripwire for unit mismatches -- these fail silently otherwise."""
    print("\nUnit / scale checks")
    problems = []
    for feat in features:
        if feat in BINARY_COLUMNS:
            bad = sorted(set(mimic[feat].dropna().unique()) - {0, 1, 0.0, 1.0})
            if bad:
                problems.append(f"{feat}: MIMIC has non-binary values {bad[:5]}")
            continue
        u_med, m_med = uci[feat].median(), mimic[feat].median()
        if feat in EXPECTED_RANGES:
            lo, hi = EXPECTED_RANGES[feat]
            if not (lo <= m_med <= hi):
                problems.append(
                    f"{feat}: MIMIC median {m_med:,.1f} outside expected "
                    f"[{lo:,}-{hi:,}] -- likely a unit mismatch")
        if u_med > 0 and m_med > 0:
            ratio = max(u_med, m_med) / min(u_med, m_med)
            flag = "  <-- CHECK UNITS" if ratio >= 5 else ""
            print(f"  {feat:26s} UCI {u_med:>12,.1f}   MIMIC {m_med:>12,.1f}"
                  f"   ratio {ratio:>5.1f}x{flag}")
            if ratio >= 5:
                problems.append(f"{feat}: medians differ {ratio:.0f}x "
                                f"(UCI {u_med:,.1f} vs MIMIC {m_med:,.1f})")
        else:
            print(f"  {feat:26s} UCI {u_med:>12,.1f}   MIMIC {m_med:>12,.1f}")
    if problems:
        print("\n  !! POSSIBLE UNIT MISMATCHES -- resolve before trusting results:")
        for p in problems:
            print(f"     - {p}")
    else:
        print("  no scale mismatches detected")


def cohort_shift_report(uci, mimic, features) -> pd.DataFrame:
    rows = [{
        "feature": f,
        "uci_mean": uci[f].mean(),
        "mimic_mean": mimic[f].mean(),
        "abs_diff": abs(uci[f].mean() - mimic[f].mean()),
        "mimic_missing_%": 100 * mimic[f].isna().mean(),
    } for f in features]
    rows.append({
        "feature": TARGET + " (rate)",
        "uci_mean": uci[TARGET].mean(),
        "mimic_mean": mimic[TARGET].mean(),
        "abs_diff": abs(uci[TARGET].mean() - mimic[TARGET].mean()),
        "mimic_missing_%": 0.0,
    })
    shift = pd.DataFrame(rows)
    print("\nCohort shift (means)")
    print(shift.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    return shift


def internal_cv(df, features, label) -> dict:
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=RANDOM_STATE)
    res = cross_validate(make_pipeline(), df[features], df[TARGET],
                         cv=cv, scoring=["roc_auc", "f1", "accuracy"], n_jobs=-1)
    out = {}
    print(f"\n{label}")
    for metric in ["roc_auc", "f1", "accuracy"]:
        arr = res[f"test_{metric}"]
        lo, hi = np.percentile(arr, [2.5, 97.5])
        out[metric] = (arr.mean(), lo, hi)
        print(f"  {metric:9s}: {arr.mean():.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    return out


def bootstrap_transfer(train, test, features, label, n_boot: int = 1000) -> dict:
    """Fit once on the full training cohort; CIs from bootstrapping the test set."""
    pipe = make_pipeline().fit(train[features], train[TARGET])
    X_test, y_test = test[features], test[TARGET].to_numpy()
    proba = pipe.predict_proba(X_test)[:, 1]
    pred = pipe.predict(X_test)
    point = {
        "roc_auc": roc_auc_score(y_test, proba),
        "f1": f1_score(y_test, pred),
        "accuracy": accuracy_score(y_test, pred),
    }
    rng = np.random.default_rng(RANDOM_STATE)
    n = len(y_test)
    boots = {m: [] for m in point}
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if len(np.unique(y_test[idx])) < 2:      # need both classes for ROC-AUC
            continue
        boots["roc_auc"].append(roc_auc_score(y_test[idx], proba[idx]))
        boots["f1"].append(f1_score(y_test[idx], pred[idx]))
        boots["accuracy"].append(accuracy_score(y_test[idx], pred[idx]))
    out = {}
    print(f"\n{label}")
    print(f"  trained on {len(train):,} rows, tested on {n:,} rows")
    for metric, value in point.items():
        lo, hi = np.percentile(boots[metric], [2.5, 97.5])
        out[metric] = (value, lo, hi)
        print(f"  {metric:9s}: {value:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="HeartGuard external validation")
    ap.add_argument("--uci", type=Path,
                    default=Path("data/heart_failure_clinical_records_dataset.csv"))
    ap.add_argument("--mimic", type=Path, required=True)
    ap.add_argument("--keep-cpk", action="store_true")
    ap.add_argument("--out", type=Path,
                    default=Path("notebooks/external_validation_results.csv"))
    args = ap.parse_args()

    print("=" * 68)
    print("HeartGuard external validation")
    print("=" * 68)
    print("\nCohorts")
    uci = load_cohort(args.uci, "UCI")
    mimic = load_cohort(args.mimic, "MIMIC")

    features = resolve_shared_features(uci, mimic, args.keep_cpk)
    check_units(uci, mimic, features)
    shift = cohort_shift_report(uci, mimic, features)

    print("\n" + "=" * 68)
    print("Baselines (internal cross-validation)")
    print("=" * 68)
    full = internal_cv(uci, UCI_FEATURES, "UCI, all 11 features (current model)")
    base = internal_cv(uci, features, f"UCI, {len(features)} shared features (fair baseline)")
    mim = internal_cv(mimic, features, f"MIMIC, {len(features)} shared features")

    print("\n" + "=" * 68)
    print("Transfer experiments")
    print("=" * 68)
    a = bootstrap_transfer(uci, mimic, features, "A) Train UCI -> test MIMIC  [primary]")
    b = bootstrap_transfer(mimic, uci, features, "B) Train MIMIC -> test UCI  [supporting]")

    rows = [
        ("UCI internal (11 features)", len(uci), len(uci), full),
        (f"UCI internal ({len(features)} shared)", len(uci), len(uci), base),
        (f"MIMIC internal ({len(features)} shared)", len(mimic), len(mimic), mim),
        ("A: UCI -> MIMIC", len(uci), len(mimic), a),
        ("B: MIMIC -> UCI", len(mimic), len(uci), b),
    ]
    results = pd.DataFrame([{
        "experiment": name, "n_train": n_tr, "n_test": n_te,
        "roc_auc": r["roc_auc"][0], "roc_auc_lo": r["roc_auc"][1],
        "roc_auc_hi": r["roc_auc"][2], "f1": r["f1"][0],
        "accuracy": r["accuracy"][0],
    } for name, n_tr, n_te, r in rows])

    print("\n" + "=" * 68)
    print("Summary")
    print("=" * 68)
    print(results.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.out, index=False)
    shift.to_csv(args.out.with_name("cohort_shift.csv"), index=False)
    print(f"\nSaved: {args.out}")
    print(f"Saved: {args.out.with_name('cohort_shift.csv')}")

    drop = base["roc_auc"][0] - a["roc_auc"][0]
    print("\n" + "-" * 68)
    print(f"Transfer gap (UCI internal -> MIMIC external): {drop:+.3f} ROC-AUC")
    if drop > 0.10:
        print("  Large drop. Consistent with cohort shift (US ICU vs Pakistani")
        print("  clinic) and/or the dropped features. Report it as a finding --")
        print("  models frequently fail to transfer across sites.")
    elif drop > 0.05:
        print("  Moderate drop -- typical for cross-site transfer.")
    else:
        print("  Small drop. The model transfers well; worth highlighting.")
    print("-" * 68)


if __name__ == "__main__":
    main()