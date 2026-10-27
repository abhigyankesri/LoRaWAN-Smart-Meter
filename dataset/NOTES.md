# Dataset Event Annotations

This document contains detailed notes about specific events and counter numbers for annotated sensor files.

## Files with "Cycled" Measurements

These files track device on/off cycles with specific counter markers for the cycled device:

### Straightener_On_hairdryer_Cycled.log
- **Hair dryer (cycled)**: Turned ON around **counter 1577**
- **Hair dryer (cycled)**: Turned OFF around **counter 1709**

### hairdryer_On_airpurifier_Cycled.log
- **Air purifier (cycled)**: Turned ON around **counter 1961**
- **Air purifier (cycled)**: Turned OFF around **counter 2167**

### Straightener_On_Purifier_Cycled.log
- **Air purifier (cycled)**: Turned ON around **counter 2331**
- **Air purifier (cycled)**: Turned OFF around **counter 2569**

### airpurifier_On_hairdryer_Cycled.log
- **Hair dryer (cycled)**: Turned ON around **counter 2836**
- **Hair dryer (cycled)**: Turned OFF around **counter 2980**

### hairdryer_On_hairstraightner_Cycled.log
- **Hair straightener (cycled)**: Turned ON around **counter 3265**
- **Hair straightener (cycled)**: Turned OFF around **counter 3462**

---

## Multi-Appliance File

### allthreeappliance.log
Simultaneous operation of three appliances (Air purifier, Hair dryer, Hair straightener) with the following event timeline:

| Counter # | Event |
|-----------|-------|
| Start | Air purifier **ON**, Hair dryer **OFF**, Hair straightener **OFF** |
| ~662 | Hair dryer turned **ON** |
| ~797 | Hair straightener turned **ON** |
| ~947 | Air purifier turned **OFF** |
| ~1116 | Air purifier turned **ON** |
| ~1215 | Hair dryer turned **OFF** |
| ~1289 | Hair dryer turned **ON** |
| ~1338 | Hair straightener turned **OFF** |
| ~1439 | Hair straightener turned **ON** |

---

## How to Use These Notes

1. **For analysis**: Use the counter numbers to locate specific events within the `.log` files
2. **For validation**: Compare power consumption patterns at the marked counter numbers with device state changes
3. **For anomaly detection**: Identify any power readings that don't match expected device behavior
4. **For machine learning**: These annotations can serve as ground truth labels for training predictive models

## Counter Definition
"Counter" refers to the sequential row number or timestamp index in the respective `.log` file, marking when a specific event occurred.
