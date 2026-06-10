"""
Experimental / optional tools for emergency_chatbot.py.

Everything here is OPTIONAL and ISOLATED:
- The chatbot imports EXTRA_TOOLS inside a try/except, so deleting this whole
  file just falls back to the 4 base tools — nothing else breaks.
- Each tool is registered in its OWN try/except block, so if one skill's script
  is missing, broken, or needs a dependency that isn't installed
  (matplotlib / fpdf2), only THAT tool is skipped — the rest still load.

Each tool reuses the project's real skill scripts in .gemini/skills/ (single
source of truth); we only wrap them as LangChain tools here.
"""

import os
import csv
import importlib.util

from langchain_core.tools import tool

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.join(ROOT, ".gemini", "skills")
# Generated artifacts (maps, PDFs) land here, out of the repo root. Gitignored.
GENERATED_DIR = os.path.join(ROOT, "instance", "generated")


def _output_path(filename):
    """Absolute path for a generated file, creating instance/generated/ on demand."""
    os.makedirs(GENERATED_DIR, exist_ok=True)
    return os.path.join(GENERATED_DIR, filename)


def _load(skill, script):
    """Load a skill script module by path (raises if the file/deps are missing)."""
    path = os.path.join(SKILLS, skill, "scripts", script)
    spec = importlib.util.spec_from_file_location(f"_xtool_{skill}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_reference(skill, filename):
    """Read a skill's vetted reference doc (.gemini/skills/<skill>/references/<filename>).
    Raises if missing so the caller's try/except disables only that tool."""
    path = os.path.join(SKILLS, skill, "references", filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def _summarize_elements(data, label):
    """Compact summary for raw Overpass JSON, to avoid flooding the model."""
    if not isinstance(data, dict) or "elements" not in data:
        return f"No {label} data (got: {data})"
    els = data["elements"]
    lines = [f"Found {len(els)} {label}."]
    for el in els[:8]:
        tags = el.get("tags", {})
        name = tags.get("name", "unnamed")
        lat, lon = el.get("lat"), el.get("lon")
        coords = f" ({lat}, {lon})" if lat and lon else ""
        lines.append(f"- {name}{coords}")
    return "\n".join(lines)


EXTRA_TOOLS = []


# rad-recon: measured radiation near coordinates
try:
    _rad = _load("rad-recon", "poll_teleray.py")

    @tool
    def radiation_here(lat: float, lon: float) -> dict:
        """Get the nearest radiation sensor reading (nSv/h) to the given coordinates,
        from the IRSN Teleray network. Use when the user asks how much radiation is
        measured at their location or wants real sensor data."""
        return _rad.get_nearest_sensor(lat, lon)

    EXTRA_TOOLS.append(radiation_here)
except Exception as e:
    print(f"[tool 'radiation_here' disabled: {e}]")


# strike-predictor: nearby military targets + urgency
try:
    _strike = _load("strike-predictor", "predict_next.py")

    @tool
    def strike_risk(lat: float, lon: float) -> list:
        """Assess strike risk: list nearby strategic military targets (East France)
        ranked by distance, each with probability and urgency. Use when the user asks
        if they are in a high-risk zone or what could be targeted near them."""
        return _strike.predict_threats(lat, lon)

    EXTRA_TOOLS.append(strike_risk)
except Exception as e:
    print(f"[tool 'strike_risk' disabled: {e}]")


# risk-analyst (offline CSV): closest nuclear plants
try:
    _risk_local = _load("risk-analyst", "local_risk_check.py")
    _PLANTS_CSV = os.path.join(SKILLS, "risk-analyst", "assets", "nuclear_plants.csv")

    @tool
    def nearby_nuclear_plants(lat: float, lon: float, limit: int = 5) -> list:
        """List the nuclear power plants closest to the given coordinates (offline
        database, distance in km). Use when the user asks about nearby nuclear plants
        or reactor proximity. Works without internet."""
        # Read the CSV by its real header; reuse the script's haversine (calculate_distance).
        plants = []
        with open(_PLANTS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    dist = _risk_local.calculate_distance(
                        lat, lon, float(row["lat"]), float(row["lon"])
                    )
                except (ValueError, KeyError):
                    continue
                plants.append({
                    "name": row.get("name", "unknown"),
                    "distance_km": round(dist, 1),
                    "reactors": row.get("reactors"),
                })
        return sorted(plants, key=lambda p: p["distance_km"])[:limit]

    EXTRA_TOOLS.append(nearby_nuclear_plants)
except Exception as e:
    print(f"[tool 'nearby_nuclear_plants' disabled: {e}]")


# risk-analyst (online Overpass): strategic sites
try:
    _risk_online = _load("risk-analyst", "query_targets.py")

    @tool
    def strategic_sites(lat: float, lon: float, radius_km: int = 50) -> str:
        """Query live OpenStreetMap data for military sites and nuclear plants near
        coordinates. Use for an up-to-date scan of strategic targets nearby (needs
        internet); for offline use prefer nearby_nuclear_plants."""
        return _summarize_elements(
            _risk_online.get_strategic_sites(lat, lon, radius_km), "strategic site(s)"
        )

    EXTRA_TOOLS.append(strategic_sites)
except Exception as e:
    print(f"[tool 'strategic_sites' disabled: {e}]")


# comms-monitor: official emergency broadcasts
try:
    _comms = _load("comms-monitor", "poll_broadcasts.py")

    @tool
    def emergency_broadcasts() -> dict:
        """Poll official emergency feeds (US NWS alerts, French Ministère de
        l'Intérieur) for the latest active alerts. Use when the user asks for news,
        official alerts, broadcasts, or what authorities are announcing."""
        return _comms.poll_feeds()

    EXTRA_TOOLS.append(emergency_broadcasts)
except Exception as e:
    print(f"[tool 'emergency_broadcasts' disabled: {e}]")


# emergency-briefer: BLUF formatted brief
try:
    _brief = _load("emergency-briefer", "format_brief.py")

    @tool
    def make_brief(status: str, primary_action: str, actions: list, mode: str = "standard") -> str:
        """Format a BLUF (Bottom Line Up Front) emergency brief from a status, a
        primary action, and a list of survival actions. mode = 'flash' (<50 words)
        or 'standard'. Use to deliver a clean final summary to the user."""
        data = {
            "status": status,
            "summary_action": primary_action,
            "primary_action": primary_action,
            "top_3_actions": actions,
        }
        return _brief.format_brief(data, mode)

    EXTRA_TOOLS.append(make_brief)
except Exception as e:
    print(f"[tool 'make_brief' disabled: {e}]")


# data-visualizer: blast-radius PNG (needs matplotlib)
try:
    _viz = _load("data-visualizer", "create_map.py")

    @tool
    def blast_map(lat: float, lon: float, yield_kt: float = 12) -> str:
        """Generate a PNG map of blast / thermal / radiation radii for a detonation
        of yield_kt kilotons at the coordinates. Returns the saved file path.
        Requires matplotlib."""
        out = _output_path("blast_map.png")
        _viz.generate_blast_map(lat, lon, yield_kt, out)
        return f"Blast map saved to {out}"

    EXTRA_TOOLS.append(blast_map)
except Exception as e:
    print(f"[tool 'blast_map' disabled: {e}]")


# pdf-generator: offline PDF brief (needs fpdf2)-
try:
    _pdf = _load("pdf-generator", "generate_report.py")

    @tool
    def emergency_pdf(impact: str, evacuation: str, poi: list) -> str:
        """Generate an offline, printable PDF survival brief (impact analysis,
        evacuation route, points of interest). Returns the saved file path.
        Requires fpdf2."""
        out = _output_path("emergency_brief.pdf")
        _pdf.generate_emergency_pdf(
            {"impact": impact, "evacuation": evacuation, "poi": poi}, output_path=out
        )
        return f"PDF brief saved to {out}"

    EXTRA_TOOLS.append(emergency_pdf)
except Exception as e:
    print(f"[tool 'emergency_pdf' disabled: {e}]")


# health-advisor (reference doc): grounded medical / decontamination protocol
try:
    @tool
    def decontamination_and_radiation_health() -> str:
        """Return the vetted nuclear/radiological MEDICAL protocol: triage,
        decontamination (remove outer clothing, lukewarm water, no scrubbing),
        Acute Radiation Syndrome phases and dose indicators (time-to-vomiting),
        countermeasures (potassium iodide / KI, Prussian Blue, DTPA), and radiation
        burns. Call this for ANY question about radiation exposure, contamination,
        decontamination, nausea/vomiting after exposure, KI, or radiation symptoms,
        then relay these steps. Do not invent medical advice."""
        return _read_reference("health-advisor", "protocols_medical.md")

    EXTRA_TOOLS.append(decontamination_and_radiation_health)
except Exception as e:
    print(f"[tool 'decontamination_and_radiation_health' disabled: {e}]")


# psych-counselor (reference doc): grounded panic / anxiety first aid
try:
    @tool
    def calming_exercise() -> str:
        """Return the vetted Psychological First Aid protocol: the 5-4-3-2-1
        grounding technique, 4-7-8 breathing, and crisis communication principles.
        Call this whenever the user is panicking, anxious, hyperventilating, can't
        breathe, or asks to be calmed down, then guide them through it."""
        return _read_reference("psych-counselor", "pfa_protocols.md")

    EXTRA_TOOLS.append(calming_exercise)
except Exception as e:
    print(f"[tool 'calming_exercise' disabled: {e}]")


if __name__ == "__main__":
    print("Loaded extra tools:", [t.name for t in EXTRA_TOOLS])
