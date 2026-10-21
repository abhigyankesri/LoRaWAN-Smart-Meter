-- UK-DALE NILM pipeline schema
-- Run once against a fresh database:
--   createdb metrology_db
--   psql metrology_db -f schema.sql

-- Raw meter feed. Written by feeder_ukdale.py, read by live_inference_ukdale.py.
CREATE TABLE device_readings (
    time                  TIMESTAMPTZ      NOT NULL,
    device_id             TEXT             NOT NULL,
    voltage_v             DOUBLE PRECISION,
    current_a             DOUBLE PRECISION,
    power_active_w        DOUBLE PRECISION,
    power_apparent_va     DOUBLE PRECISION,
    energy_accumulator_wh DOUBLE PRECISION
);

CREATE INDEX device_readings_time_idx ON device_readings (time);

-- Classifier output. Written by live_inference_ukdale.py, read by Grafana.
CREATE TABLE appliance_state (
    time      TIMESTAMPTZ      NOT NULL,
    appliance TEXT             NOT NULL,
    state     TEXT             NOT NULL,
    power_w   DOUBLE PRECISION
);

CREATE INDEX appliance_state_time_idx ON appliance_state (time);
