---
name: risk-analyst
description: Assesses the risk of a specific location based on proximity to strategic military, political, or economic targets. Use when a user asks about the safety of a location or wants to know if they are in a high-risk zone.
---

# Risk Analyst

Determines the vulnerability of a location to a nuclear strike.

## Workflow

1.  **Identify Targets**: 
    - Use `scripts/query_targets.py` to fetch real-time data on military bases and nuclear plants from Overpass API.
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
- **Scripts**: `scripts/query_targets.py` handles API interaction.

## Target Reference

See [references/targets.md](references/targets.md) for target categorization.
