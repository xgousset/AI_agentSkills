---
name: resource-inventory
description: Manages tracking of essential survival supplies and identifies nearby acquisition points. Use when the user asks about supplies, food, water, potassium iodide (KI), inventory status, or where to find pharmacies, supermarkets, or drinking-water points.
---

# Resource Inventory

Facilitates long-term survival by managing critical assets.

## Workflow

1.  **Inventory Tracking**: Maintain a list of personal supplies (water, food, KI, radio).
2.  **Point of Interest (POI) Search**: Use `scripts/find_resources.py` to query Overpass API for `amenity=pharmacy`, `shop=supermarket`, and `amenity=drinking_water` within a configurable radius (default 5 km) around the user's coordinates.
3.  **Consumption Modeling**: Estimate remaining survival time based on current inventory.

## Data Sources
- **Overpass API**: Live queries for `amenity=pharmacy`, `shop=supermarket`, `amenity=drinking_water`.

## Scripts
- `scripts/find_resources.py` — fetches nearby POIs from Overpass. Takes `(lat, lon, radius_km)`; returns the raw Overpass JSON.
