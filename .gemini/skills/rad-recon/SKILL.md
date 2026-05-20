# Radiological Reconnaissance

Simulates or integrates real-time radiation sensor data to map contamination with high precision.

## Workflow
1. **Sensor Integration**: Polls public radiation monitoring networks (e.g., IRSN Teleray in France).
2. **Dynamic Isopleths**: Generates real-time radiation intensity maps (isopleths) based on actual readings vs. theoretical models.
3. **Hot-Zone Identification**: Identifies localized "hotspots" that may differ from general fallout models due to rain or terrain.

## Resources
- `scripts/poll_teleray.py`: (Planned) Fetches real-time sensor data from public networks.
- `references/dose_thresholds.md`: Safe vs. Lethal dose guidelines.
