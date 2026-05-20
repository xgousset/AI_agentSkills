import json
import sys
import xml.etree.ElementTree as ET

import requests

USER_AGENT = "GeminiEmergencyAgent/1.0 (nuclear-emergency-skills)"

FEEDS = [
    {
        "name": "NWS Alerts (US)",
        "url": "https://api.weather.gov/alerts/active",
        "format": "geojson",
    },
    {
        "name": "Ministère de l'Intérieur (FR)",
        "url": "https://www.interieur.gouv.fr/rss/actu.xml",
        "format": "rss",
    },
]


def _parse_rss(content):
    root = ET.fromstring(content)
    items = []
    for item in root.findall(".//item")[:3]:
        items.append(
            {
                "title": (item.find("title").text or "").strip(),
                "link": (item.find("link").text or "").strip(),
            }
        )
    return items


def _parse_geojson(content):
    data = json.loads(content)
    items = []
    for feature in data.get("features", [])[:3]:
        props = feature.get("properties", {})
        items.append(
            {
                "title": props.get("headline") or props.get("event", "Unknown alert"),
                "link": props.get("@id", ""),
                "severity": props.get("severity"),
            }
        )
    return items


def poll_feeds():
    """Polls a list of official emergency feeds, returning entries + errors."""
    alerts = []
    errors = []
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json, application/rss+xml, */*"}

    for feed in FEEDS:
        try:
            response = requests.get(feed["url"], headers=headers, timeout=10)
        except requests.RequestException as exc:
            errors.append({"source": feed["name"], "error": f"network: {exc.__class__.__name__}"})
            continue

        if response.status_code != 200:
            errors.append({"source": feed["name"], "error": f"http {response.status_code}"})
            continue

        try:
            if feed["format"] == "rss":
                items = _parse_rss(response.content)
            elif feed["format"] == "geojson":
                items = _parse_geojson(response.content)
            else:
                errors.append({"source": feed["name"], "error": f"unknown format {feed['format']}"})
                continue
        except (ET.ParseError, json.JSONDecodeError, ValueError) as exc:
            errors.append({"source": feed["name"], "error": f"parse: {exc.__class__.__name__}"})
            continue

        for item in items:
            item["source"] = feed["name"]
            alerts.append(item)

    return {"alerts": alerts, "errors": errors}


if __name__ == "__main__":
    result = poll_feeds()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # Non-zero exit if every feed failed — useful for monitoring.
    if not result["alerts"]:
        sys.exit(2)
