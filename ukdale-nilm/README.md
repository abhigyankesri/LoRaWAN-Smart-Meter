# UK-DALE NILM

Non-intrusive load monitoring on the UK-DALE dataset. A single aggregate power
signal is streamed into Postgres, split into appliance activations, and each
activation is classified with a random forest. Results are written to a second
table for Grafana to display.

Appliances: fridge, microwave, washing machine, lighting, TV.

## Pipeline

```
prepare_ukdale.py   raw UK-DALE channels  ->  per-appliance CSVs (60s)
train_eval_..._ukdale.py   CSVs  ->  ukdale_activation_classifier.joblib
feeder_ukdale.py    CSVs summed into one aggregate  ->  device_readings
live_inference_ukdale.py   device_readings  ->  appliance_state  ->  Grafana
```

The feeder deliberately discards which appliance is which — it sums all five
into one number, the way a real house meter would see it. The inference script
then has to work backwards from that single signal.

## Model

`RandomForestClassifier(n_estimators=300, class_weight='balanced')`

Each activation is reduced to four features:

| Feature | Meaning | Importance |
|---|---|---|
| `peak_power` | largest instantaneous draw | 0.40 |
| `mean_power` | typical draw over the run | 0.23 |
| `power_std` | steady vs. swinging | 0.21 |
| `duration_s` | burst vs. long cycle | 0.16 |

`class_weight='balanced'` is set because activation counts are very uneven —
a fridge cycles dozens of times a day, a washing machine runs once.

## Setup

### 1. Get the data

Download UK-DALE House 1 from
<https://jack-kelly.com/data/> and place the channel files in a folder named
`ukdale/`. The dataset is not redistributed here.

Channels used (from `labels.dat`):

| Appliance | Channel |
|---|---|
| washing machine | 5 |
| tv | 7 |
| fridge | 12 |
| microwave | 13 |
| lighting | 25 |

### 2. Install

```bash
pip install -r requirements.txt
```

scikit-learn is pinned because the shipped `.joblib` was serialized under that
version. Loading it under a different one may produce wrong results.

### 3. Create the database

```bash
createdb metrology_db
psql metrology_db -f schema.sql
```

Set your connection details as environment variables:

```bash
export PGHOST=localhost
export PGDATABASE=metrology_db
export PGUSER=postgres
export PGPASSWORD=...
```

## Running

```bash
python prepare_ukdale.py                    # ukdale/ -> ukdale_prepared/
python train_eval_activations_ukdale.py     # -> ukdale_activation_classifier.joblib
python feeder_ukdale.py                     # terminal 1
python live_inference_ukdale.py             # terminal 2
```

The feeder and inference script run at the same time — one writes, the other
reads. A pre-trained model is included, so steps 1 and 2 can be skipped if you
only want to watch the live demo.

## Known limitations

Worth stating plainly, since they affect how the results should be read:

- **Train/serve mismatch.** The classifier is trained on isolated appliance
  activations but applied to an aggregate signal. When two appliances overlap,
  the extracted features describe a mixture the model never saw in training.
- **Single-label output.** Exactly one of five classes is always returned.
  There is no "off", no "unknown", and no way to report two appliances at once.
  Prediction confidence is not currently thresholded.
- **Fixed segmentation threshold.** Activations are split on a 150 W drop.
  A fridge switching off (~100 W) falls below this and is not detected as a
  boundary; a microwave switching off (~1400 W) ends the run for every
  appliance, including ones still running.
- **Synthetic electrical quantities.** UK-DALE provides watts only. Apparent
  power, power factor and current are placeholders (`S = P`, `PF = 1`,
  `I = P/230`) and carry no independent information.
- **No off events.** Only `'on'` rows are written to `appliance_state`.

The natural next step is to reframe this as multi-label per-timestep
disaggregation, or to move to an edge-based classifier that keys on step
changes rather than whole runs — both handle overlap without the segmentation
heuristic.

## Files

```
prepare_ukdale.py                      data prep
train_eval_activations_ukdale.py       training + evaluation
feeder_ukdale.py                       synthetic meter
live_inference_ukdale.py               detector + classifier
ukdale_activation_classifier.joblib    trained model (21 MB)
schema.sql                             Postgres tables
requirements.txt
```

## Dataset

Kelly, J. and Knottenbelt, W. (2015). The UK-DALE dataset, domestic
appliance-level electricity demand and whole-house demand from five UK homes.
*Scientific Data* 2:150007.
