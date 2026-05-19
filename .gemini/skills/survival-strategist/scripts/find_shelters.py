import requests
import json

def get_shelters(lat, lon, radius_km=20):
    """
    Queries Overpass API for public shelters near a location.
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    radius = radius_km * 1000
    
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="shelter"]["shelter_type"~"bomb|nuclear"](around:{radius},{lat},{lon});
      way["amenity"="shelter"]["shelter_type"~"bomb|nuclear"](around:{radius},{lat},{lon});
      node["bunker_type"](around:{radius},{lat},{lon});
      way["bunker_type"](around:{radius},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    headers = {
        "User-Agent": "GeminiEmergencyAgent/1.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(overpass_url, data={'data': query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Overpass API error: {response.status_code}"}

if __name__ == "__main__":
    # Example: Besançon coordinates
    besancon_lat, besancon_lon = 47.2378, 6.0244
    shelters = get_shelters(besancon_lat, besancon_lon)
    print(json.dumps(shelters, indent=2))
