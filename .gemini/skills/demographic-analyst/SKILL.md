---
name: demographic-analyst
description: Assesses population density and identifies vulnerable groups (hospitals, schools, nursing homes) requiring prioritized assistance. Use when the user asks about population density, crowding risk, evacuation priorities, vulnerable people (elderly, children, disabled), or pediatric/geriatric supply demand.
---

# Demographic Risk Analyst

Assesses population density and identifies vulnerable groups requiring prioritized assistance.

## Workflow
1. **Density Mapping**: Identify high-density residential zones prone to mass-panic or resource depletion.
2. **Vulnerability Assessment**: Map locations of hospitals, nursing homes, and schools.
3. **Resource Allocation**: Predict demand for pediatric/geriatric medical supplies based on local demographics.

## Resources
- `assets/pop_vulnerability.csv`: Regional data on specialized care facilities.
- `scripts/analyze_density.py`: Correlates population data with blast radii.

## Data Sources
- **INSEE (Population & Stats)**: https://www.insee.fr/fr/statistiques/3568638, https://api.insee.fr/, https://statistiques-locales.insee.fr/
