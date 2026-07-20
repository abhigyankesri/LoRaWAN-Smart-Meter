"""
live_inference_ukdale.py
------------------------
Watches device_readings, detects appliance ACTIVATIONS in the UK-DALE stream,
classifies them with the UK-DALE activation model, and writes results to
appliance_state for Grafana.

Because the UK-DALE model is ACTIVATION-based (not edge-based), this tracks when
the aggregate rises into a run and, when it settles/ends, classifies that run's
duration + power + variability. It also does a simple "which appliance dominates
now" readout for the live panel.

Run:  python live_inference_ukdale.py   (Ctrl+C to stop)
Requirements: pip install pandas scikit-learn joblib psycopg2-binary
"""
import time
import numpy as np
import pandas as pd
import joblib
import psycopg2

DB = dict(host="localhost", port="5432", dbname="metrology_db",
          user="postgres", password="meterpass123")
MODEL = "ukdale_activation_classifier.joblib"
FEATURES = ["duration_s", "mean_power", "peak_power", "power_std"]

# per-appliance rough power (for the live "what's on" readout + attribution)
SIG = {
    "fridge": 100, "microwave": 1400, "washing_machine": 500,
    "lighting": 300, "tv": 120,
}
ON_FLOOR = 20.0
POLL = 1.0

clf = joblib.load(MODEL)
print(f"Loaded {MODEL}. Appliances: {list(clf.classes_)}")


def classify(buf):
    """buf = list of (time, power) samples for one activation run."""
    ts = [t for t, _ in buf]; ps = np.array([p for _, p in buf], float)
    dur = (ts[-1] - ts[0]).total_seconds()
    X = pd.DataFrame([[dur, ps.mean(), ps.max(), ps.std()]], columns=FEATURES)
    return clf.predict(X)[0]


def main():
    conn = psycopg2.connect(**DB); conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT max(time) FROM device_readings;")
    last = cur.fetchone()[0] or pd.Timestamp("1970-01-01", tz="UTC")

    run = []            # current activation buffer
    prevP = None
    DROP = 150.0        # a power drop bigger than this = an appliance switched off
    print("Watching device_readings (UK-DALE)...  (Ctrl+C to stop)\n")

    def flush(run, cur):
        if len(run) >= 2:
            appliance = classify(run)
            power = float(round(np.mean([p for _, p in run]), 1))
            cur.execute("""INSERT INTO appliance_state (time, appliance, state, power_w)
                           VALUES (%s,%s,'on',%s)""", (run[-1][0], appliance, power))
            print(f"{run[-1][0]:%H:%M:%S}  detected {appliance:16s} ({power:.0f}W)")

    while True:
        cur.execute("""SELECT time, power_active_w FROM device_readings
                       WHERE time > %s ORDER BY time;""", (last,))
        for t, P in cur.fetchall():
            last = t; P = float(P)
            # a big DROP from the previous reading = current run ended -> classify
            if prevP is not None and (prevP - P) >= DROP and len(run) >= 2:
                flush(run, cur); run = []
            if P >= ON_FLOOR:
                run.append((t, P))
            elif len(run) >= 2:
                flush(run, cur); run = []
            prevP = P
        time.sleep(POLL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")