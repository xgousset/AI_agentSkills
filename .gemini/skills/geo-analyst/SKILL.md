---
name: geo-analyst
description: Analyzes terrain features (rivers, mountains) and transit infrastructure (bridges, tunnels, walled areas) to find bottlenecks and accessible safe zones. Use when the user asks about routes, terrain obstacles, bridges/tunnels status, or accessibility for mobility-impaired individuals.
---

# Geo-Accessibility Analyst

Analyzes geographic features and infrastructure accessibility to identify bottlenecks and safe zones.

## Workflow
1. **Terrain Analysis**: Identify natural barriers (rivers, mountains) and human-made ones (walled areas, closed gates).
2. **Access Audit**: Monitor the status of bridges, tunnels, and main transit arteries.
3. **Accessibility Mapping**: Identify wheelchair-accessible shelters and routes for mobility-impaired individuals.

## Resources
- `assets/transit_nodes.json`: Database of key bridges and tunnels.
- `scripts/map_barriers.py`: Analyzes OSM data for transit interruptions.

## Data Sources
- **IGN Géoplateforme (Data.geopf)**: https://data.geopf.fr/ (Authoritative French geographic data).
- **Panoramax**: https://panoramax.fr/ (Street-level imagery).
- **API Adresse**: https://api-adresse.data.gouv.fr/
- **API Géo**: https://geo.api.gouv.fr/
