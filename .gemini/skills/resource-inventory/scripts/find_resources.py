import requests
import json

def get_resources(lat, lon, radius_km=5):
    """
    Finds essential supply points (pharmacies, supermarkets, water) using Overpass API.
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    radius = radius_km * 1000
    
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="pharmacy"](around:{radius},{lat},{lon});
      node["shop"="supermarket"](around:{radius},{lat},{lon});
      node["amenity"="drinking_water"](around:{radius},{lat},{lon});
    );
    out body;
    """
    
    headers = {"User-Agent": "GeminiEmergencyAgent/1.0"}
    response = requests.post(overpass_url, data={'data': query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return {"error": response.status_code}

if __name__ == "__main__":
    # Example: Besançon
    print(json.dumps(get_resources(47.24, 6.02), indent=2))
