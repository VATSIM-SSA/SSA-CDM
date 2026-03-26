# SSA-CDM

VATSSA Collaborative Decision Making (CDM) Configuration Management

## Overview

This repository stores CDM configuration data for airports within the VATSIM SSA division. The data is organized by FIR (Flight Information Region) and controls departure sequencing, runway rates, SID separation, and taxi zone definitions.

## Repository Structure

```
├── FASA/          # South Africa FIR
│   ├── CTOT.txt        # Slot-controlled event assignments
│   ├── rate.txt        # Runway configuration and acceptance rates
│   ├── sidinterval.txt # SID pair separation intervals
│   └── taxizones.txt   # Taxi zone polygon definitions
├── HKNA/          # Nairobi FIR
│   ├── CTOT.txt
│   ├── rate.txt
│   ├── sidinterval.txt
│   └── taxizones.txt
└── validate.py    # Data validation script
```

## File Formats

### CTOT.txt — Slot-Controlled Events

Assigns a Calculated Take-Off Time (CTOT) to a specific pilot during slot-controlled events.

```
[CID],[CTOT]
```

- **CID** — VATSIM Client ID
- **CTOT** — Calculated Take-Off Time (HHMM UTC)

### rate.txt — Runway Configurations & Rates

Defines runway configurations and the associated arrival/departure acceptance rates.

```
AIRPORT:A:ArrRwyList:NotArrRwyList:D:DepRwyList:NotDepRwyList:DependentRwyList:Rate_RateLvo
```

| Field | Description |
|---|---|
| AIRPORT | ICAO airport code |
| A | Arrival indicator |
| ArrRwyList | Active arrival runway(s) |
| NotArrRwyList | Inactive arrival runways |
| D | Departure indicator |
| DepRwyList | Active departure runway(s) |
| NotDepRwyList | Inactive departure runways |
| DependentRwyList | Runways with dependent operations |
| Rate_RateLvo | Normal rate and Low Visibility Operations rate, separated by `_` |

### sidinterval.txt — SID Separation Intervals

Defines the minimum separation (in minutes) between successive departures using specific SID pairs from the same runway.

```
<ICAO_Airport>,<dep_rwy>,<SID1>,<SID2>,<separation_minutes>
```

### taxizones.txt — Taxi Zone Polygons

Defines geographic polygons for taxi/apron zones, used to estimate taxi times.

```
AIRPORT:RUNWAY:LAT1:LON1:LAT2:LON2:LAT3:LON3:LAT4:LON4:ZONE_ID
```

Coordinates use degrees/minutes/seconds format (e.g., `S026.06.43.951:E028.28.21.024`).

## Adding a New FIR

1. Create a new directory named with the ICAO FIR identifier (e.g., `FAJA`)
2. Add the four data files: `CTOT.txt`, `rate.txt`, `sidinterval.txt`, `taxizones.txt`
3. Populate each file following the formats documented above
4. Run `python validate.py` to check for errors before committing

## Validation

Run the validation script to check all data files for formatting errors:

```bash
python validate.py
```

The script checks:
- Correct number of fields per line
- Valid ICAO airport codes (4 uppercase letters A-Z)
- Numeric rate values are positive integers
- SID separation values are positive integers

## Current FIRs

| Directory | FIR | Airports | Status |
|---|---|---|---|
| `FASA` | South Africa | FAOR, FACT, FALE, FALA, FAGG, FAPE, FAEL, FABL | Complete |
| `HKNA` | Nairobi | HKJK | Partial — rate data only |
