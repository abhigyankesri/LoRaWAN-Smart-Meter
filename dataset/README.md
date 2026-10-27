# Smart Meter Dataset

This folder contains sensor meter logs from various household appliances tracked via LoRaWAN.

## File Categories

### 1. Single Appliance Measurements
- `ecookerHIGH.log` - Electric cooker at high setting
- `ecookerLOW.log` - Electric cooker at low setting
- `mixerHIGH.log` - Mixer at high speed
- `mixerMED.log` - Mixer at medium speed
- `mixerLOW.log` - Mixer at low speed
- `hairstraighter.log` - Hair straightener single operation
- `hairstraighterplusfanspeed1.log` - Hair straightener + air purifier fan speed 1
- `hairstraightnerplusairpurifierfanspeed2.log` - Hair straightener + air purifier fan speed 2
- `hairstraightnerplusairpurifierfanspeed3.log` - Hair straightener + air purifier fan speed 3

### 2. Cycled Appliance Pairs (With Event Annotations)
These files contain sequential device operations with specific counter markers:
- `Straightener_On_hairdryer_Cycled.log` - [See NOTES.md]
- `hairdryer_On_airpurifier_Cycled.log` - [See NOTES.md]
- `Straightener_On_Purifier_Cycled.log` - [See NOTES.md]
- `hairdryer_On_hairstraightner_Cycled.log` - [See NOTES.md]
- `airpurifier_On_hairdryer_Cycled.log` - [See NOTES.md]

### 3. Multi-Appliance Data
- `allthreeappliance.log` - Simultaneous operation of all three appliances with detailed event timeline [See NOTES.md]

### 4. Hair Dryer Temperature Variants
- `hairdryer_cold.log` - Hair dryer in cold mode
- `hairdryer_warm.log` - Hair dryer in warm mode
- `hairdryer_warmest.log` - Hair dryer in hottest mode

### 5. Hair Dryer + Purifier Combinations
- `hairdryerLOW_purifierHIGH.log` - Low hairdryer + High purifier
- `hairdryerLOW_purifierLOW.log` - Low hairdryer + Low purifier
- `hairdryerLOW_purifierMED.log` - Low hairdryer + Medium purifier
- `hairdryerMED_purifierLOW.log` - Medium hairdryer + Low purifier

## Data Format
Each `.log` file contains timestamped sensor readings from the LoRaWAN smart meter, capturing power consumption and other metrics at regular intervals.

## Important Notes
For files with event annotations, please refer to `NOTES.md` for specific counter numbers indicating device state changes.
