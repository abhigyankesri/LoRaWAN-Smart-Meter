"""
feeder_ukdale.py
----------------
Streams the UK-DALE aggregate (fridge+microwave+washing_machine+lighting+tv)
into device_readings, impersonating the meter. Feeds the live UK-DALE demo.

Run:  python feeder_ukdale.py   (Ctrl+C to stop)
Requirements: pip install pandas psycopg2-binary
"""
import time
import os
import psycopg2
import numpy as np
import pandas as pd

DB = dict(host="localhost", port="5432", dbname="metrology_db",
          user="postgres", password="meterpass123")
PREP_DIR = "ukdale_prepared"
APPLIANCES = ["fridge", "microwave", "washing_machine", "lighting", "tv"]
DEVICE_ID = "ukdale-demo"
SLEEP = 0.4       # seconds between inserts (demo pace)
MAINS_V = 230.0


def build_aggregate():
    dfs = {}
    for n in APPLIANCES:
        dfs[n] = pd.read_csv(f"{PREP_DIR}/{n}.csv", parse_dates=["time"],
                             index_col="time").sort_index()
    idx = None
    for df in dfs.values():
        idx = df.index if idx is None else idx.union(df.index)
    P = pd.Series(0.0, index=idx)
    for df in dfs.values():
        P = P.add(df["P"].reindex(idx).fillna(0.0), fill_value=0.0)
    agg = pd.DataFrame({"P": P}, index=idx.sort_values())
    return agg[agg["P"] >= 60]   # only stream rows with real appliance activity


def main():
    conn = psycopg2.connect(**DB); conn.autocommit = True
    cur = conn.cursor()
    agg = build_aggregate()
    print(f"Loaded {len(agg)} UK-DALE aggregate rows. Streaming... (Ctrl+C to stop)\n")
    energy = 0.0
    now = pd.Timestamp.utcnow()
    n = 0
    for _, row in agg.iterrows():
        P = float(row["P"]); V = 230.0 if P > 0 else 0.0
        I = P / MAINS_V
        energy += P * (60.0 / 3600.0)   # 60s of Wh
        now = now + pd.Timedelta(seconds=60)
        cur.execute(
            """INSERT INTO device_readings
               (time, device_id, voltage_v, current_a, power_active_w,
                power_apparent_va, energy_accumulator_wh)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (now, DEVICE_ID, V, I, P, P, energy))
        n += 1
        if n % 5 == 0:
            print(f"  {n:5d} rows fed | latest P={P:7.1f} W")
            time.sleep(SLEEP)
    print(f"\nDone. Fed {n} rows.")
    cur.close(); conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")