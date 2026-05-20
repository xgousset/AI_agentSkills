---
name: rad-recon
description: Integrates real-time radiation sensor data (IRSN Teleray in France, equivalent networks elsewhere) to map actual contamination and identify hot-zones that differ from theoretical fallout models due to rain or terrain. Use when the user asks for measured radiation readings, sensor-based maps, or to validate theoretical fallout predictions against ground truth.
---

# Radiological Reconnaissance

Simulates or integrates real-time radiation sensor data to map contamination with high precision.

## Workflow
1. **Sensor Integration**: Polls public radiation monitoring networks (e.g., IRSN Teleray in France).
2. **Dynamic Isopleths**: Generates real-time radiation intensity maps (isopleths) based on actual readings vs. theoretical models.
3. **Hot-Zone Identification**: Identifies localized "hotspots" that may differ from general fallout models due to rain or terrain.

## Resources
- `scripts/poll_teleray.py`: (Planned) Fetches real-time sensor data from public networks.
- `references/dose_thresholds.md`: Safe vs. Lethal dose guidelines.
