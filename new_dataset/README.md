# New Dataset – Appliance Switching Log (LoRaWAN Smart Meter)

Labelled smart-meter readings recorded while four household loads were switched ON/OFF in a known sequence. Every row carries the meter's RMS voltage, RMS current, active power and energy reading, plus ground-truth ON/OFF flags for each appliance, so the file can be used to check appliance-level (load identification) experiments against known events.

Part of the [LoRaWAN-Smart-Meter](https://github.com/abhigyankesri/LoRaWAN-Smart-Meter) project.

## Experiment setup

- **Start:** 2:36 – all devices off (clock time as noted at the start of the run; the date was not recorded).
- **Loads under test:**
  - Hair dryer
  - Hair straightener
  - 200 W bulb
  - 100 W bulb
- **Events:** each change of state was noted by hand against the meter's *Measurement Counter* (the sample index printed in the serial log). The log file begins at counter 361 and ends at 5905.
- **Sampling interval:** not recorded, so counters are not converted to seconds.

## Files

| File | Description |
|---|---|
| `new_dataset.csv` | 5,545 rows, one per measurement counter (361–5905, no gaps or duplicates), with appliance labels |

## Columns

| Column | Unit | Description |
|---|---|---|
| `counter` | – | Measurement Counter from the meter log |
| `voltage_V` | V | RMS voltage |
| `current_A` | A | RMS current |
| `power_W` | W | Active power (raw value as logged) |
| `energy_Wh` | Wh | Active energy register (raw cumulative value as logged) |
| `hair_dryer` | 0/1 | Hair dryer ON |
| `hair_straightener` | 0/1 | Hair straightener ON |
| `bulb_200W` | 0/1 | 200 W bulb ON |
| `bulb_100W` | 0/1 | 100 W bulb ON |
| `num_devices_on` | 0–4 | Sum of the four flags |
| `segment` | 1–18 | Index of the timeline segment below |
| `power_glitch` | 0/1 | 1 if `power_W` is a bad reading (see Data notes) |

## Timeline

Labels switch at the counters noted during the run. "Observed step" is where the measured power actually changes; it is shown so you can see how closely the manual notes line up (Δ is shown only when the difference is more than 1 counter). Median power excludes glitch rows and the first 10 samples of each segment.

| Seg | Counters | Samples | Hair dryer | Straightener | 200 W bulb | 100 W bulb | Observed step | Median power (W) |
|---|---|---|---|---|---|---|---|---|
| 1 | 361–387 | 27 | – | – | – | – | start of log | 1 |
| 2 | 388–617 | 230 | – | – | ON | – | 385 (Δ-3) | 224 |
| 3 | 618–874 | 257 | ON | – | ON | – | 619 | 1708 |
| 4 | 875–1266 | 392 | ON | – | – | – | 876 | 1500 |
| 5 | 1267–1591 | 325 | ON | ON | – | – | 1267 | 1617 |
| 6 | 1592–2054 | 463 | – | ON | – | – | 1592 | 82 |
| 7 | 2055–2415 | 361 | – | ON | ON | – | 2054 | 301 |
| 8 | 2416–2884 | 469 | – | ON | – | – | 2417 | 76 |
| 9 | 2885–3384 | 500 | – | ON | – | ON | 2885 | 204 |
| 10 | 3385–3793 | 409 | – | – | – | ON | 3384 | 130 |
| 11 | 3794–4335 | 542 | ON | – | – | ON | 3793 | 1632 |
| 12 | 4336–4497 | 162 | ON | – | – | – | 4335 | 1510 |
| 13 | 4498–5016 | 519 | ON | – | ON | ON | 4497 | 1847 |
| 14 | 5017–5344 | 328 | – | – | ON | ON | 5016 | 356 |
| 15 | 5345–5566 | 222 | – | ON | ON | ON | 5350 (Δ+5) | 484 |
| 16 | 5567–5840 | 274 | ON | ON | ON | ON | 5567 | 1928 |
| 17 | 5841–5884 | 44 | – | – | ON | ON | 5840 | 353 |
| 18 | 5885–5905 | 21 | – | – | – | – | 5883 (Δ-2) | 2 |

## Data notes

- **Bad power readings:** 15 rows have `power_W` around 3,015,459 W (5 in segment 1, 10 in segment 18). They only occur while everything is off and current is ~0.09 A, so they look like a meter read/overflow error. The raw values are kept and flagged with `power_glitch = 1`; drop them before analysis.
- **Label timing:** labels follow the manually noted counters. The measured switching points differ by up to a few counters in three places: the 200 W bulb turn-on (noted 388, power rises at 385), the straightener turn-on (noted 5345, power rises at 5350) and the final all-off (noted 5885, power drops at 5883). Shift the labels to the observed step if you need sample-accurate edges.
- **Switch-on transients:** the straightener draws a short inrush spike when switched on (e.g. 7.6 A at counter 5351) and then decays as it heats, so its power is not constant within a segment. The hair dryer settles at roughly 1.5 kW.
- **Energy register:** `energy_Wh` is the raw cumulative counter (9 at counter 361, 133,294 at 5905). It rises by about 6 per sample at ~225 W, which is not obviously consistent with the sampling interval, so verify calibration before using absolute energy values.
- **Ranges:** voltage 242.3–248.6 V; current 0.09–11.11 A.

## Loading the data

```python
import pandas as pd

df = pd.read_csv("new_dataset.csv")
clean = df[df.power_glitch == 0]
print(clean.groupby("segment")["power_W"].median())
```
