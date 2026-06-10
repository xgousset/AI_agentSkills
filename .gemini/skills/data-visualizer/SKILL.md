---
name: data-visualizer
description: Transforms complex spatial and technical data into clear visual representations (fallout heatmaps, blast-radius overlays, supply dashboards). Use when the user asks to plot, visualize, render a map, generate a chart, or produce graphical output from emergency data.
---

# Survival Data Visualizer

Transforms complex spatial and technical data into clear, actionable visual representations.

## Workflow
1. **Fallout Mapping**: Generate heatmaps of radiation intensity.
2. **Radius Visualization**: Render concentric blast zones over a **real OpenStreetMap basemap** using `scripts/create_map.py` — accepts `lat`, `lon`, and `yield_kt`; outputs a PNG file. The thermal / blast / prompt-radiation circles are drawn as translucent overlays on top of actual streets. Falls back to a tile-less rendering if offline.
3. **Resource Dashboard**: Create visual charts of supply levels and shelter capacity.
4. **Export Engine**: Support exporting all visualizations as high-compression PNG/JPG files for embedding in PDF reports.

## Scripts
- `scripts/create_map.py` — generates a blast-radius overlay (thermal, blast wave, prompt radiation circles) over a real OpenStreetMap basemap for a given detonation point. Uses `staticmap` (OSM tiles) + Pillow (translucent overlay); output is a PNG.

## Tools
- **staticmap + Pillow**: Real OSM basemap with translucent geographic circles, exported as PNG.
- **Matplotlib**: For non-geographic charts (supply levels, dashboards).
