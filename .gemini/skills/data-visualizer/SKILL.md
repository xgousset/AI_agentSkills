---
name: data-visualizer
description: Transforms complex spatial and technical data into clear visual representations (fallout heatmaps, blast-radius overlays, supply dashboards). Use when the user asks to plot, visualize, render a map, generate a chart, or produce graphical output from emergency data.
---

# Survival Data Visualizer

Transforms complex spatial and technical data into clear, actionable visual representations.

## Workflow
1. **Fallout Mapping**: Generate heatmaps of radiation intensity.
2. **Radius Visualization**: Render concentric blast zones over local maps using `scripts/create_map.py` — accepts `lat`, `lon`, and `yield_kt`; outputs a PNG file.
3. **Resource Dashboard**: Create visual charts of supply levels and shelter capacity.
4. **Export Engine**: Support exporting all visualizations as high-compression PNG/JPG files for embedding in PDF reports.

## Scripts
- `scripts/create_map.py` — generates a Matplotlib blast-radius overlay (thermal, blast wave, prompt radiation circles) for a given detonation point.

## Tools
- **Matplotlib/Plotly**: For generating charts and static maps.
- **Folium**: For interactive geographic visualizations (exportable via selenium/imgkit).
