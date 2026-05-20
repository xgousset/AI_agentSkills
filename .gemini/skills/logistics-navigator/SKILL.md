---
name: logistics-navigator
description: Optimizes evacuation routing to avoid radioactive fallout, fire zones, and bottlenecks; computes Safe-Exit vectors perpendicular to the plume. Use when the user asks for an evacuation route, safe-exit path, turn-by-turn directions out of a danger zone, or how to drive away from the fallout.
---

# Logistics Navigator

Optimizes evacuation routing to avoid radioactive fallout and high-risk zones.

## Workflow

1.  **Map Obstacles**: Identify blast zones, fire zones, and predicted fallout plumes.
2.  **Calculate Vectors**: Determine "Safe-Exit" paths perpendicular to the fallout trajectory.
3.  **Identify Bottlenecks**: Factor in traffic density and known bridge/tunnel collapses.
4.  **Advise**: Provide turn-by-turn evacuation instructions with real-time updates based on wind shifts.

## Data Sources

- **OpenStreetMap**: For routing and bridge data.
- **Fallout Predictor**: For dynamic plume data.

## Scripts

- `scripts/calculate_evac.py`: (Planned) Generates safe-exit routes cross-referenced with fallout data.
