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
    - Wind speed and direction at different altitudes (surface, 5000m, 10000m).
2.  **Analyze**:
    - Determine the 'Hotline' (center of the fallout plume).
    - Estimate the width and length of the plume based on yield and wind speed.
    - Identify 'Contamination Zones' (Extreme, High, Moderate, Low).
3.  **Advise**:
    - Provide immediate sheltering instructions for areas in the predicted path.
    - Estimate 'Time of Arrival' (TOA) for different locations.

## Reference Material

Refer to [references/physics.md](references/physics.md) for detailed formulas and particle settling rates.
