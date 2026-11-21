# Appliance-detection dataset – 21 Nov 2026

BTP Energy Meter (X-NUCLEO-PM33A1 / STPM33 on NUCLEO-G071RB, firmware v0.3.0), recorded on 21 Nov 2026 following the
"BTP Energy Meter – Appliance Data Collection Protocol".

Four appliances: **hair dryer**, **hair straightener**, **200 W bulb**, **100 W bulb**. Every one of the 16 on/off
combinations is present.

| File | What it is |
|---|---|
| `*.log` | Raw Tera Term captures of the meter's serial console (unchanged) |
| `labelled_dataset.csv` | All valid samples from the logs, parsed, with appliance labels (1,370 rows) – **use this for ML** |
| `switch_events.csv` | Every switch (148 events): when, which appliance, ON/OFF, and whether it came from the notes or was read from the data |
| `README.md` | This file |

---

## 1. How the data was recorded

- The meter takes one measurement per second. `counter` is the sample number = **seconds since the board booted**.
- The serial console prints **every 5th sample** (counter 130, 135, 140, …). So the logs have a **5-second resolution**;
  short spikes (e.g. the straightener's switch-on surge) are caught only if they fall on a printed sample.
- Each log line looks like:
  `[meter] #2750 V=248.42 V  I=0.514 A  P=130.5 W  PF=0.983  f=49.98 Hz  E=51.173 Wh  heap=16584`
  (voltage, current, active power, power factor, frequency, energy since boot in **Wh**, free RAM).
- Lines starting with `[ERROR] ... ST67W6XTask` are Wi-Fi module messages. They do not affect the measurements – no
  samples are missing in any file (the counter always steps by 5).
- **The board was restarted between the two runs, so the counter starts again from 0 in Run 2.** Always identify a
  sample by `(run, counter)`, never by counter alone.

## 2. Files, in recording order

Clock times are estimated from the file save times (counter 0 ≈ 03:55:04 for Run 1 and ≈ 17:23:40 for Run 2, IST).

### Run 1 – early morning (≈ 03:57 – 05:05)

| File | Counter | ≈ Time | Protocol block | Contents | Use |
|---|---|---|---|---|---|
| `alldevicesoff3min.log` | 130–305 | 03:57–04:00 | – | All off **but mains not connected** (V = 0.03 V, frequency is noise) | **Exclude** (only shows the 0.098 A current offset) |
| `alldevicesoff_final_3mins.log` | 340–520 | 04:00–04:04 | A. Baseline | All off, mains connected | Train |
| `straightnerdata.log` | 570–1565 | 04:05–04:21 | C. Straightener heat-up | Cold start for 10 min, then **3** hot restarts (protocol said 5) | Train |
| `lookalikepair.log` | 1795–2475 | 04:25–04:36 | D. Look-alike pair | 100 W and hot straightener alternating ×4, then both together | Train |
| `singlecycles.log` | 2745–3840 | 04:41–04:59 | B. Single cycles | 100 W, 200 W, dryer: 30 s on / 30 s off ×6 each | Train |
| `pause.log` | 3905–4190 | 05:00–05:05 | Pause | All off | Train |

Not recorded in Run 1: counters 525–565, 1570–1790, 2480–2740, 3845–3900 (gaps between files).

### Run 2 – evening (≈ 17:27 – 18:45)

| File | Counter | ≈ Time | Protocol block | Contents | Use |
|---|---|---|---|---|---|
| `teraterm.log` | 205–2875 | 17:27–18:11 | E. Combination tours | Tours 1–4, exactly as in the protocol (64 switches, 40 s apart) | Train |
| `testingdataset.log` | 4000–4910 | 18:30–18:45 | F. Free use | Irregular household-style switching (20 switches) | **Test only – never train on it** |

Tour boundaries in `teraterm.log`: Tour 1 = 205–840, Tour 2 = 845–1500, Tour 3 = 1505–2200, Tour 4 = 2205–2875.
Not recorded in Run 2: counters 0–200 and 2880–3995.

## 3. `labelled_dataset.csv` columns

| Column | Meaning |
|---|---|
| `run` | 1 = morning, 2 = evening |
| `source_file` | Log the row came from |
| `block` | `A_baseline`, `C_straightener`, `D_lookalike`, `B_single_cycles`, `pause`, `E_tour1`…`E_tour4`, `F_test` |
| `split` | `train` or `test` (test = `testingdataset.log`) |
| `counter` | Sample number (seconds since boot, restarts per run) |
| `voltage_V`, `current_A`, `power_W`, `pf`, `freq_Hz` | Measurements |
| `energy_Wh` | Energy since boot in Wh (real Wh, unlike the old dataset's 10 mWh units) |
| `hair_dryer`, `hair_straightener`, `bulb_200W`, `bulb_100W` | 1 = on, 0 = off |
| `num_devices_on` | Sum of the four labels |
| `transition` | 1 for the sample where a switch first shows and the one after it (may contain switch-on surges or settling) |
| `dryer_medium_setting` | 1 for counters 3705–3735 in Run 1, when the dryer was on MEDIUM by mistake (~900 W) |

**Label rule:** a switch is labelled at the **first logged sample that shows the change**. The real switch happened
somewhere in the 5 seconds before it.

**Check:** for every non-transition row, the measured power matches the sum of the labelled appliances' typical power
to within 120 W, so no rows appear mislabelled.

Rows per combination (dryer, straightener, 200 W, 100 W): every one of the 16 combinations has 32–355 rows.

## 4. `switch_events.csv` columns

`run, block, counter, appliance, action (ON/OFF), source, note`.
`source` is `noted` (from the handwritten log) or `inferred from data` (counter missing from the notes, taken from the
power step).

### Corrections to the handwritten notes

| Run | Noted | Used | Why |
|---|---|---|---|
| 1 | (missing) | 575 straightener ON | Cold start was not written down; step clearly visible (457 W surge) |
| 1 | 1485 straightener ON | 1490 | Step appears at 1490 |
| 1 | 1800 100 W ON | 1795 | Bulb already on in the first logged sample |
| 1 | 1930 100 W ON | 1925 | Step appears at 1925 |
| 1 | 2180 100 W ON | 2175 | Step appears at 2175 |
| 1 | 2745 100 W ON | 2745 | Bulb already on in the first logged sample of `singlecycles.log` |
| 2 | Tour 1 "100W bulb on" (no counter) | 205 | Bulb already on in the first logged sample of `teraterm.log` |
| 2 | 1350 200 W OFF | 1345 | Step appears at 1345 |
| 2 | 4585 dryer OFF | 4580 | Step appears at 4580 |

All other noted counters match the data exactly.

## 5. Measured signatures (steady state, firmware v0.3.0, 241–250 V, 49.8–50.2 Hz)

| Appliance (alone) | Power (median, range) | PF | Current |
|---|---|---|---|
| All off | 0.5 W (−3 to 4 W) | noise | 0.098 A (sensor offset) |
| 100 W bulb | 129 W (125–135 W) | 0.995–1.000 | 0.51 A |
| 200 W bulb | 227 W (222–231 W) | 1.000 | 0.91 A |
| Hair dryer (normal setting) | 1,491 W (1,454–1,512 W) | 1.000 | 6.09 A |
| Hair dryer (medium, mistake) | 902 W | 0.962 | 3.82 A |
| Hair straightener | 116 W (97–213 W) | ≈ 0.96 | 0.49 A |

**Straightener behaviour (the key to telling it apart from the 100 W bulb):**
- Cold start: a surge of about 457 W at switch-on, then power falls steadily as it heats:
  ~213 W after 10 s, ~154 W after 1 min, ~132 W after 2 min, ~112 W after 5 min, ~105 W after 10 min.
- Hot restarts also show a short surge in the first sample (seen from about 200 W up to about 1,550 W above the
  background), then settle to about 110–130 W within 5–10 s.
- Its PF is about 0.94–0.99, while the bulbs read 0.995–1.000.
- When hot, its power (~105–130 W) overlaps the 100 W bulb (~129 W), so power alone cannot separate them.

## 6. Known limitations

- 5-second resolution (serial log), not the 1-second dashboard CSV; reactive power Q and apparent power S are not in
  the logs.
- Current is measured in ~20 mA steps with a 0.098 A offset at no load.
- Only 3 straightener hot restarts instead of 5; one dryer cycle at the wrong setting (flagged).
- One recording session; for a stronger test, record a second day (the protocol's "recommended" plan).

## 7. How to use it for training

- Train on `split == "train"`, report accuracy on `split == "test"` only.
- For model selection, use leave-one-block-out (or leave-one-tour-out) cross-validation, **not** a random row split –
  neighbouring rows are near-copies and a random split overstates accuracy.
- Consider dropping or separately handling `transition == 1` rows for a snapshot classifier; keep them for an
  event-based model.
- The old dataset (`new_dataset.csv`, previous firmware/vendor firmware) is not part of this folder. If used at all, use
  it only as an extra test with V/I/P features, after removing its `power_glitch` rows.
