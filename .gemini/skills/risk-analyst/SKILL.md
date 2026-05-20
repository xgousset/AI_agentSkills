---
name: risk-analyst
description: Assesses the risk of a specific location based on proximity to strategic military, political, or economic targets. Use when a user asks about the safety of a location or wants to know if they are in a high-risk zone.
---

# Risk Analyst

Determines the vulnerability of a location to a nuclear strike.

## Workflow

1.  **Identify Targets**:
    - **Online (preferred)**: Use `scripts/query_targets.py` to fetch real-time data on military bases and nuclear plants from Overpass API.
    - **Offline fallback**: If Overpass is unreachable (timeout, 5xx), use `scripts/local_risk_check.py`, which reads [`assets/nuclear_plants.csv`](assets/nuclear_plants.csv) (GPPD-format global database of nuclear power plants) and returns the closest plants by Haversine distance.
    - Cross-reference with [references/targets.md](references/targets.md).
2.  **Calculate Distance**: Use the Great Circle distance to nearest targets.
3.  **Score Risk**:
    - **Critical**: < 10km from a high-priority target (Counter-force).
    - **High**: 10-30km from a target.
    - **Moderate**: 30-70km from a target.
    - **Low**: > 70km from any major strategic site.
4.  **Consider Secondary Risks**: EMP impact on infrastructure, power grid failure.

## Data Sources

- **Overpass API (OpenStreetMap)**: Live queries for `military=base` and `power=plant`.
- **Scripts**:
  - `scripts/query_targets.py` — online path via Overpass.
  - `scripts/local_risk_check.py` — offline fallback over the bundled CSV.

## Resources

- **Target categorization**: [references/targets.md](references/targets.md)
- **Offline plant database**: [assets/nuclear_plants.csv](assets/nuclear_plants.csv) — GPPD v1.3 schema (country_code, country, name, gppd_id, capacity_mw, latitude, longitude, ...).
