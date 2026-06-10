"""Blast-radius visualization over a REAL OpenStreetMap basemap.

Renders concentric impact circles (blast wave / thermal / prompt radiation) as
translucent overlays on top of actual streets, using `staticmap` for the OSM tiles
and Pillow for the translucent overlay. Output is a PNG (same as before), so the
`blast_map` tool and the PDF brief keep working unchanged.

Falls back to a plain (tile-less) rendering if the tiles can't be fetched (offline),
so the function never hard-fails.
"""

import math

from PIL import Image, ImageDraw, ImageFont
from staticmap import StaticMap

TILE_SIZE = 256
EARTH_CIRCUMFERENCE_M = 40075016.686  # at the equator
# Be a good OSM citizen: identify the client (tile usage policy asks for a real UA).
USER_AGENT = "NuclearEmergencyAgent/1.0 (educational project)"

# Impact rings: (label, color RGB). Drawn largest-first so smaller rings stay visible.
RINGS = [
    ("Blast wave (moderate)", (220, 50, 50)),
    ("Thermal radiation", (255, 140, 0)),
    ("Prompt radiation", (40, 90, 230)),
]


def _load_font(size):
    """A readable TrueType font, cross-platform (DejaVu ships with matplotlib)."""
    try:
        from matplotlib import font_manager
        return ImageFont.truetype(font_manager.findfont("DejaVu Sans"), size)
    except Exception:
        return ImageFont.load_default()


def _world_px(lon, lat, zoom):
    """Web Mercator: (lon, lat) -> global pixel coords at this zoom (tile_size 256)."""
    n = TILE_SIZE * (2 ** zoom)
    x = (lon + 180.0) / 360.0 * n
    lat_rad = math.radians(lat)
    y = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n
    return x, y


def _fit_zoom(lat, max_radius_km, size_px, margin=1.35):
    """Pick the zoom where the largest ring (with margin) spans the image."""
    span_m = 2 * max_radius_km * 1000 * margin
    meters_per_px_needed = span_m / size_px
    z = math.log2(EARTH_CIRCUMFERENCE_M * math.cos(math.radians(lat)) /
                  (TILE_SIZE * meters_per_px_needed))
    return max(1, min(18, int(math.floor(z))))


def _circle_lonlat(lat, lon, radius_km, n=120):
    """Approximate a geographic circle as a polygon of (lon, lat) vertices."""
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * math.cos(math.radians(lat)))
    return [(lon + dlon * math.cos(2 * math.pi * i / n),
             lat + dlat * math.sin(2 * math.pi * i / n)) for i in range(n)]


def generate_blast_map(lat, lon, yield_kt, output_path="blast_map.png"):
    """Generate a PNG of blast radii over a real OSM map at the detonation point."""
    # Rough radii (km) — same approximation as before.
    thermal_radius = 1.5 * (yield_kt / 12) ** 0.5
    blast_radius = 2.5 * (yield_kt / 12) ** 0.33
    radiation_radius = 0.8 * (yield_kt / 12) ** 0.5
    radii = {
        "Blast wave (moderate)": blast_radius,
        "Thermal radiation": thermal_radius,
        "Prompt radiation": radiation_radius,
    }

    W = H = 800
    zoom = _fit_zoom(lat, max(radii.values()), W)

    # 1. Real basemap from OSM tiles (fallback to a blank canvas if offline).
    try:
        smap = StaticMap(W, H, url_template="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                         headers={"User-Agent": USER_AGENT})
        base = smap.render(zoom=zoom, center=[lon, lat]).convert("RGBA")
        offline = False
    except Exception as e:
        print(f"[map tiles unavailable ({e}); rendering without basemap]")
        base = Image.new("RGBA", (W, H), (235, 235, 230, 255))
        offline = True

    # 2. Project (lon, lat) -> image pixels, anchored on the centered detonation point.
    cx, cy = _world_px(lon, lat, zoom)

    def to_img(p_lon, p_lat):
        wx, wy = _world_px(p_lon, p_lat, zoom)
        return (wx - cx + W / 2, wy - cy + H / 2)

    # 3. Translucent rings on an overlay, largest first so smaller stays on top.
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for label, color in sorted(RINGS, key=lambda r: -radii[r[0]]):
        poly = [to_img(lo, la) for lo, la in _circle_lonlat(lat, lon, radii[label])]
        draw.polygon(poly, fill=color + (70,), outline=color + (255,))

    # Ground zero marker.
    gz = to_img(lon, lat)
    draw.line([(gz[0] - 9, gz[1]), (gz[0] + 9, gz[1])], fill=(0, 0, 0, 255), width=3)
    draw.line([(gz[0], gz[1] - 9), (gz[0], gz[1] + 9)], fill=(0, 0, 0, 255), width=3)

    image = Image.alpha_composite(base, overlay)

    # 4. Title bar + legend.
    draw = ImageDraw.Draw(image)
    font = _load_font(14)
    title_font = _load_font(16)

    title = f"{yield_kt} kt detonation  —  ({lat:.4f}, {lon:.4f})"
    if offline:
        title += "  [offline: no basemap]"
    draw.rectangle([0, 0, W, 30], fill=(0, 0, 0, 170))
    draw.text((10, 7), title, fill=(255, 255, 255, 255), font=title_font)

    legend_h = 24 * len(RINGS) + 12
    draw.rectangle([0, H - legend_h, 230, H], fill=(0, 0, 0, 150))
    for i, (label, color) in enumerate(RINGS):
        yy = H - legend_h + 8 + i * 24
        draw.rectangle([10, yy, 28, yy + 16], fill=color + (200,), outline=(255, 255, 255, 255))
        draw.text((36, yy + 1), f"{label}  ({radii[label]:.1f} km)",
                  fill=(255, 255, 255, 255), font=font)

    image.convert("RGB").save(output_path)
    print(f"Blast map generated at: {output_path}")


if __name__ == "__main__":
    # Test for Besancon
    generate_blast_map(47.2455, 6.0209, 12)
