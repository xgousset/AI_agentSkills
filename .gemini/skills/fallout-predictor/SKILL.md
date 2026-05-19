---
name: fallout-predictor
description: Predicts radioactive fallout trajectory and contamination zones based on meteorological data (wind speed, direction) and detonation parameters. Use when a user needs to know where fallout will settle after a nuclear event.
---

# Fallout Predictor

Use this skill to calculate and visualize potential radioactive fallout patterns.

## Workflow

1.  **Gather Data**:
    - Detonation location (coordinates or city).
    - Yield (in kilotons/megatons) - default to 150kt if unknown.
    - **Wind Data**: Use `scripts/get_weather.py` to fetch current wind speed and direction at different altitudes via **Open-Meteo API**.
2.  **Analyze**:
    - Determine the 'Hotline' (center of the fallout plume).
    - Estimate the width and length of the plume based on yield and wind speed.
    - Identify 'Contamination Zones' (Extreme, High, Moderate, Low).
3.  **Advise**:
    - Provide immediate sheltering instructions for areas in the predicted path.
    - Estimate 'Time of Arrival' (TOA) for different locations.

## Data Sources

- **Open-Meteo API**: Free, real-time atmospheric data (wind at various altitudes).
- **Scripts**: `scripts/get_weather.py` automates data collection.

## Reference Material

Refer to [references/physics.md](references/physics.md) for detailed formulas and particle settling rates.
