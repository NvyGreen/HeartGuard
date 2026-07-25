"""
Leakage audit + cross-validated evaluation for HeartGuard.

Quantifies how much the `time` (follow-up duration) feature inflates
performance, and reports 95% confidence intervals from repeated
stratified k-fold CV rather than a single train/test split.

Run: python notebooks/evaluate_leakage.py
"""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate

DATA = Path(__file__).resolve().parents[1] / "data" / "heart_failure_clinical_records_dataset.csv"

BASE_FEATURES = [
    "age", "anaemia", "creatinine_phosphokinase", "diabetes", "ejection_fraction",
    "high_blood_pressure", "platelets", "serum_creatinine", "serum_sodium", "sex", "smoking",
]
TARGET = "DEATH_EVENT"
SCORING = ["accuracy", "roc_auc", "f1", "precision", "recall"]


def make_pipeline():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=100, class_weight="balanced",
            max_depth=3, min_samples_leaf=15, random_state=42)),
    ])


def load_data():
    df = pd.read_csv(DATA)
    if "patient_id" in df.columns:
        df = df.drop(columns=["patient_id"])
    return df


def evaluate(df, features, label):
    # 5 folds x 20 repeats = 100 out-of-fold estimates per metric.
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=42)
    res = cross_validate(make_pipeline(), df[features], df[TARGET],
                         cv=cv, scoring=SCORING, n_jobs=-1)
    print(f"\n=== {label} ({len(features)} features) ===")
    summary = {}
    for m in SCORING:
        arr = res[f"test_{m}"]
        lo, hi = np.percentile(arr, [2.5, 97.5])
        summary[m] = (arr.mean(), arr.std(), lo, hi)
        print(f"  {m:10s}: {arr.mean():.3f}  95% CI [{lo:.3f}, {hi:.3f}]  (sd {arr.std():.3f})")
    return summary


def leakage_report(df):
    feats = BASE_FEATURES + ["time"]
    pipe = make_pipeline().fit(df[feats], df[TARGET])
    imp = pd.Series(pipe.named_steps["model"].feature_importances_, index=feats)
    imp = imp.sort_values(ascending=False)
    print("\n=== Feature importance WITH `time` included ===")
    print(imp.round(3).to_string())
    print(f"\n  `time` importance share : {imp['time']:.1%}")
    print(f"  corr(time, DEATH_EVENT) : {df['time'].corr(df[TARGET]):.3f}")
    means = df.groupby(TARGET)["time"].mean()
    print(f"  mean follow-up (survived): {means[0]:.0f} days")
    print(f"  mean follow-up (deceased): {means[1]:.0f} days")
    print("  -> `time` is truncated by the outcome and is undefined at real")
    print("     prediction time; it is excluded from the deployed model.")


def main():
    df = load_data()
    no_time = evaluate(df, BASE_FEATURES, "WITHOUT time (deployed model)")
    with_time = evaluate(df, BASE_FEATURES + ["time"], "WITH time (leakage test)")
    print("\n=== Inflation from including `time` (with - without) ===")
    for m in SCORING:
        print(f"  {m:10s}: {with_time[m][0] - no_time[m][0]:+.3f}")
    leakage_report(df)


if __name__ == "__main__":
    main()