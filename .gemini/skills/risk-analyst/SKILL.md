---
name: risk-analyst
description: Assesses the risk of a specific location based on proximity to strategic military, political, or economic targets. Use when a user asks about the safety of a location or wants to know if they are in a high-risk zone.
---

# Risk Analyst

Determines the vulnerability of a location to a nuclear strike.

## Workflow

1.  **Identify Targets**: Cross-reference user location with known strategic sites.
2.  **Calculate Distance**: Use the Great Circle distance to nearest targets.
3.  **Score Risk**:
    - **Critical**: < 10km from a high-priority target (Counter-force).
    - **High**: 10-30km from a target.
    - **Moderate**: 30-70km from a target.
    - **Low**: > 70km from any major strategic site.
4.  **Consider Secondary Risks**: EMP impact on infrastructure, power grid failure.

## Target Reference

See [references/targets.md](references/targets.md) for target categorization.
