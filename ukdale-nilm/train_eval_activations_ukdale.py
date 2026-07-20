"""
train_eval_activations_ukdale.py
--------------------------------
Watts-only activation classifier for UK-DALE (India-grid, 230V/50Hz).
Same activation approach as train_eval_activations.py, but WITHOUT power factor
(UK-DALE is watts-only). Features: duration, mean/peak power, variability.

Reads ukdale_prepared/ (made by prepare_ukdale.py).
Run:  python train_eval_activations_ukdale.py
Requirements: pip install pandas scikit-learn joblib
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

PREP_DIR = "ukdale_prepared"
APPLIANCES = ["lighting", "microwave", "washing_machine", "fridge", "tv"]

ON_POWER_W = 20.0        # lower floor -- UK-DALE has small loads (lights, tv)
MERGE_GAP_S = 300
MIN_DURATION_S = 120
TRAIN_FRAC = 0.70

# NOTE: no mean_pf here -- UK-DALE is watts-only
FEATURES = ["duration_s", "mean_power", "peak_power", "power_std"]
MODEL_OUT = "ukdale_activation_classifier.joblib"


def extract_activations(df, on_power=ON_POWER_W,
                        merge_gap_s=MERGE_GAP_S, min_duration_s=MIN_DURATION_S):
    d = df.sort_index()
    p = d["P"].to_numpy(dtype=float)
    times = d.index
    n = len(p)
    if n == 0:
        return pd.DataFrame()
    on = (p >= on_power).astype(np.int8)
    diff = np.diff(on)
    starts = list(np.where(diff == 1)[0] + 1)
    ends = list(np.where(diff == -1)[0])
    if on[0] == 1:
        starts = [0] + starts
    if on[-1] == 1:
        ends = ends + [n - 1]
    merged = []
    for a, b in zip(starts, ends):
        if merged and (times[a] - times[merged[-1][1]]).total_seconds() <= merge_gap_s:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    rows = []
    for a, b in merged:
        seg = p[a:b + 1]
        dur = (times[b] - times[a]).total_seconds()
        if dur < min_duration_s:
            continue
        rows.append({
            "start": times[a],
            "duration_s": dur,
            "mean_power": float(np.nanmean(seg)),
            "peak_power": float(np.nanmax(seg)),
            "power_std": float(np.nanstd(seg)),
        })
    return pd.DataFrame(rows)


def main():
    frames = []
    for name in APPLIANCES:
        path = os.path.join(PREP_DIR, f"{name}.csv")
        if not os.path.exists(path):
            print(f"!! missing {path}; skipping {name}")
            continue
        df = pd.read_csv(path, parse_dates=["time"], index_col="time").sort_index()
        acts = extract_activations(df)
        acts["appliance"] = name
        print(f"  {name:16s}: {len(acts):6d} activations")
        frames.append(acts)

    data = pd.concat(frames, ignore_index=True).dropna(subset=FEATURES)
    data = data.sort_values("start").reset_index(drop=True)

    cut = data["start"].quantile(TRAIN_FRAC)
    train = data[data["start"] < cut]
    test = data[data["start"] >= cut]
    print(f"\nSplit at {cut}  |  train {len(train)}  test {len(test)}")

    clf = RandomForestClassifier(n_estimators=300, random_state=42,
                                 class_weight="balanced", n_jobs=-1)
    clf.fit(train[FEATURES], train["appliance"])

    pred = clf.predict(test[FEATURES])
    print("\n--- UK-DALE activation classification (held-out) ---")
    print(classification_report(test["appliance"], pred, zero_division=0))

    labels = sorted(data["appliance"].unique())
    cm = pd.DataFrame(confusion_matrix(test["appliance"], pred, labels=labels),
                      index=[f"true_{l}" for l in labels],
                      columns=[f"pred_{l}" for l in labels])
    print("Confusion matrix:\n", cm.to_string())

    print("\nFeature importances:",
          dict(zip(FEATURES, clf.feature_importances_.round(3))))

    joblib.dump(clf, MODEL_OUT)
    print(f"\nSaved model -> {MODEL_OUT}")


if __name__ == "__main__":
    main()