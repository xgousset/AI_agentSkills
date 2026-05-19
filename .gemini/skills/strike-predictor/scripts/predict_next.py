import json
import math

# Load local target data from risk-analyst assets
TARGETS_FILE = ".gemini/skills/risk-analyst/assets/nuclear_plants.csv"

def predict_threats(user_lat, user_lon):
    """
    Identifies nearby Tier 1 and Tier 2 targets and ranks them by probability.
    """
    # Hardcoded Strategic Military Bases (East France)
    military_targets = [
        {"name": "BA 116 Luxeuil (Airbase)", "lat": 47.78, "lon": 6.33, "tier": 1},
        {"name": "Camp Valdahon", "lat": 47.15, "lon": 6.34, "tier": 1},
        {"name": "Besançon (Regional Command)", "lat": 47.24, "lon": 6.02, "tier": 2},
        {"name": "Dijon (BA 102)", "lat": 47.27, "lon": 5.09, "tier": 1}
    ]
    
    predictions = []
    
    for target in military_targets:
        # Simple Haversine-like distance
        dist = math.sqrt((target['lat'] - user_lat)**2 + (target['lon'] - user_lon)**2) * 111
        
        probability = "HIGH" if target['tier'] == 1 else "MODERATE"
        if dist < 50:
            urgency = "IMMEDIATE"
        else:
            urgency = "ELEVATED"
            
        predictions.append({
            "target": target['name'],
            "dist_km": round(dist, 1),
            "probability": probability,
            "urgency": urgency
        })
        
    return sorted(predictions, key=lambda x: x['dist_km'])

if __name__ == "__main__":
    # Test for Vesoul area
    print(json.dumps(predict_threats(47.65, 6.15), indent=2))
