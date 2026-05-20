# Scripts Usage Guide (Pense-bête)

## 1. Geocoding (`geocoding.js`)
Convert city name to coordinates.
**Usage:** `node geocoding.js <city_name>`
**Example:** `node geocoding.js "Paris"`

## 2. Map Retrieval (`get_map.js`)
Fetch static map image.
**Usage:** `node get_map.js <lat> <lon> [zoom] [width] [height]`
**Example:** `node get_map.js 48.85 2.34 12 600 450`

## 3. Weather Data (`get_weather.js`)
Get real-time wind data at different altitudes.
**Usage:** `node get_weather.js <lat> <lon>`
**Example:** `node get_weather.js 48.85 2.34`

---
**Note:** Always use quotes for city names with spaces. Coordinates must be decimal.
