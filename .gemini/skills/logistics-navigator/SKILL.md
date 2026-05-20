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
