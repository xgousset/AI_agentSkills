---
name: strike-predictor
description: Predicts potential subsequent targets based on strike patterns, geopolitical importance, and military doctrine. Use when the user asks what is next, where the next strike might land, how the conflict could escalate, or to anticipate counter-force vs counter-value targeting near a given location.
---

# Strike Predictor

Anticipates the "Next Move" in a nuclear exchange to allow for preemptive evacuation or sheltering.

## Workflow

1.  **Map Initial Strike**: Identify the nature of the first strike (e.g., Tactical/Vesoul).
2.  **Doctrine Analysis**: 
    - **Counter-force**: Is the enemy targeting silos/bases?
    - **Counter-value**: Is the enemy targeting cities/economy?
3.  **Proximity Analysis**: Use `scripts/predict_next.py` to identify the highest-probability targets within 200km of the user.
4.  **Threat Escalation**: Update the `emergency-briefer` with "Predicted Next Targets."

## Geopolitical Tiers

| Tier | Target Type | Example (Region) |
| :--- | :--- | :--- |
| **Tier 1** | Strategic Military | BA 116 Luxeuil (Airbase), Valdahon (Camp) |
| **Tier 2** | Political/Comm | Regional Prefectures, Telecom Hubs |
| **Tier 3** | Economic/Energy | Nuclear Plants (Fessenheim/Bugey), Major Industry |

## Resources
- **Target Patterns**: [references/doctrine.md](references/doctrine.md)
