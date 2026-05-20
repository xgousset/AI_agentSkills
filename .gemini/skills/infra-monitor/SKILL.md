# Infrastructure Monitor

Assists in mapping and assessing the status of critical infrastructure during and after a nuclear event.

## Workflow

1.  **Identify Assets**: Map nearby water towers, power substations, gas distribution hubs, and telecommunications towers.
2.  **Assess Status**: Correlate asset locations with blast radii and fire zones.
3.  **Prioritize Repairs**: Identify critical nodes required for basic survival (e.g., potable water pumps).
4.  **Advise**: Provide instructions on manual shut-off procedures or identifying contaminated water sources.

## Data Sources

- **Overpass API**: For mapping infrastructure nodes.
- **Project Datasets**: Local CSV/JSON files of critical facilities.

## Scripts

- `scripts/check_infra.py`: (Planned) Cross-references location with known infrastructure and blast damage.
