---
name: resource-inventory
description: Manages tracking of essential survival supplies and identifies nearby acquisition points.
---

# Resource Inventory

Facilitates long-term survival by managing critical assets.

## Workflow

1.  **Inventory Tracking**: Maintain a list of personal supplies (water, food, KI, radio).
2.  **Point of Interest (POI) Search**: Use Overpass API to find pharmacies, supermarkets, and water sources.
3.  **Consumption Modeling**: Estimate remaining survival time based on current inventory.

## Data Sources
- **Overpass API**: Live queries for `amenity=pharmacy`, `shop=supermarket`, `amenity=drinking_water`.
