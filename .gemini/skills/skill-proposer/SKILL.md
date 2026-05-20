---
name: skill-proposer
description: Analyzes project requirements and current capabilities to suggest new specialized skills. Use when the user asks what is missing from the agent, requests a gap analysis, or wants to propose / brainstorm a new skill.
---

# Skill Proposer

Assists in the expansion of the agent's emergency response suite by identifying missing domains.

## Workflow

1.  **Analyze Context**: Run `scripts/analyze_gaps.py` to scan `.gemini/skills/` and diff the current catalog against the **Domains of Expertise** listed in `GEMINI.md` (Geography, Demography, Geopolitics, Economics, Equipment and Infrastructure, Survival Protocols, Public Health, Data Visualization, Meteorology, News and Information Feeds). The script returns structured proposals for any uncovered domain.
2.  **Generate Concept**: Take the script's output and propose a refined skill name, description (with explicit "Use when..." trigger), and high-level workflow.
3.  **Outline Structure**: Define the necessary scripts, references, and assets required for the new skill.

## Scripts
- `scripts/analyze_gaps.py` — capability gap analysis. Reads the skills folder, maps existing skills to GEMINI.md domains, returns proposals for missing ones.

## Guidelines

- Focus on **High-Impact** survival domains.
- Ensure the proposed skill doesn't overlap significantly with existing ones.
- Prioritize skills that can utilize available APIs or local datasets.
