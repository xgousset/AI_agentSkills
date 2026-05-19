---
name: survival-strategist
description: Provides critical survival guidance, evacuation routes, and shelter locations during a nuclear emergency. Use when a user asks for immediate actions to take, where to go, or how to prepare for an imminent or ongoing nuclear event.
---

# Survival Strategist

Empowers the agent to guide users through life-saving decisions in a nuclear crisis.

## Workflow

1.  **Assess Situation**:
    - Current user location.
    - Time since event (if occurred).
    - Proximity to immediate danger (blast radius).
2.  **Determine Action**:
    - **Shelter-in-Place**: If blast is imminent or fallout is arriving.
    - **Evacuate**: If there is time to move out of the predicted fallout path.
3.  **Provide Instructions**:
    - **Find Shelters**: Use `scripts/find_shelters.py` to query Overpass API for `amenity=shelter`.
    - Specific evacuation routes (cross-wind).
    - Shelter types (underground, concrete buildings).
    - Necessary supplies (water, food, radio).

## Data Sources

- **Overpass API**: Live query for bomb and nuclear shelters.
- **Scripts**: `scripts/find_shelters.py` fetches local shelter data.

## Resources

- **Protocols**: [references/protocols.md](references/protocols.md)
- **Shelters**: [assets/shelters.json](assets/shelters.json)
