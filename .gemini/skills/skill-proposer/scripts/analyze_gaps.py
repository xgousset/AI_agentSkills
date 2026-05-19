import os
import json

def analyze_capabilities():
    """
    Scans the .gemini/skills directory and identifies missing emergency domains
    based on the project objectives in GEMINI.md.
    """
    current_skills = os.listdir('.gemini/skills')
    
    # Domains defined in GEMINI.md
    target_domains = [
        "Geography", "Demography", "Geopolitics", "Economics",
        "Equipment and Infrastructure", "Survival Protocols",
        "Public Health", "Data Visualization", "Meteorology",
        "News and Information Feeds"
    ]
    
    # Mapping existing skills to domains (simplified)
    coverage = {
        "Geography": "location-provider",
        "Meteorology": "fallout-predictor",
        "Public Health": "health-advisor",
        "Survival Protocols": "survival-strategist",
        "Infrastructure": "risk-analyst"
    }
    
    missing = [d for d in target_domains if d not in coverage and d.lower() not in [s.lower() for s in current_skills]]
    
    proposals = []
    if "News and Information Feeds" in missing:
        proposals.append({
            "name": "comms-monitor",
            "description": "Monitors emergency broadcast systems and local news feeds.",
            "reason": "Critical for real-time situational awareness during a blackout or event."
        })
    
    if "Economics" in missing or "Equipment" in missing:
        proposals.append({
            "name": "resource-inventory",
            "description": "Tracks local availability of food, fuel, and medical supplies.",
            "reason": "Vital for long-term survival planning post-initial blast."
        })

    return proposals

if __name__ == "__main__":
    print(json.dumps(analyze_capabilities(), indent=2))
