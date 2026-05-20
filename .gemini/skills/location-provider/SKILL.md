---
name: location-provider
description: Retrieves the user's current geographic location based on IP address or system data. Essential for providing localized emergency guidance. Use when any other skill needs the user's coordinates (lat/lon) or when the user asks where they are, what city they are in, or to confirm their location.
---

# Location Provider

This skill enables the agent to determine the user's current coordinates, city, and region.

## Workflow

1.  **Geolocation**: Use `scripts/get_location.py` to fetch coordinates.
2.  **Validation**: Verify the accuracy of the location (check for VPN or proxy anomalies).
3.  **Handoff**: Provide coordinates (latitude, longitude) to other skills (e.g., Fallout Predictor, Risk Analyst).

## Data Sources

- **IP-API.com**: Free geolocation service based on public IP address.
- **System IP**: Retrieved via external lookup.

## Scripts

- `scripts/get_location.py`: Main Python script for geolocation retrieval.
