"""
prepare_ukdale.py
-----------------
Load UK-DALE House 1 channel files into the clean schema our pipeline uses.

UK-DALE format: each channel_N.dat is two space-separated columns:
    <unix_timestamp> <watts>
sampled ~every 6 seconds. WATTS ONLY -- no apparent power, no power factor.
labels.dat maps channel number -> appliance name.
UK is 230V/50Hz, matching India.

We resample to 60s and output P (and derive S=P, PF=1, I=P/230 as placeholders,
since only watts exist -- the watts-only trainer ignores PF anyway).

Run:  python prepare_ukdale.py
Requirements: pip install pandas
"""

import os
import pandas as pd

RAW_DIR = "ukdale"
OUTPUT_DIR = "ukdale_prepared"
RESAMPLE_RULE = "60s"
MAINS_V = 230.0

# appliance name -> channel number (from labels.dat)
CHANNELS = {
    "lighting":        25,
    "microwave":       13,
    "washing_machine": 5,
    "fridge":          12,
    "tv":              7,
}


def load_channel(channel):
    path = os.path.join(RAW_DIR, f"channel_{channel}.dat")
    df = pd.read_csv(path, sep=r"\s+", header=None, names=["t", "P"])
    s = pd.Series(df["P"].to_numpy(dtype=float),
                  index=pd.to_datetime(df["t"], unit="s"))
    s.index.name = "time"
    return s.sort_index()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, ch in CHANNELS.items():
        path = os.path.join(RAW_DIR, f"channel_{ch}.dat")
        if not os.path.exists(path):
            print(f"!! skipping {name}: {path} not found")
            continue
        p = load_channel(ch).resample(RESAMPLE_RULE).mean().dropna()
        out = pd.DataFrame({
            "P": p.values,
            "S": p.values,              # watts-only: no real apparent power
            "PF": 1.0,                  # placeholder (trainer ignores PF)
            "I": p.values / MAINS_V,
        }, index=p.index)
        out.index.name = "time"
        dest = os.path.join(OUTPUT_DIR, f"{name}.csv")
        out.to_csv(dest)
        span = f"{out.index.min()} -> {out.index.max()}"
        print(f"{name:16s} (ch {ch:2d}): {len(out):7d} rows  ({span})  -> {dest}")


if __name__ == "__main__":
    main()