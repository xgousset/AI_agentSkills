import requests
import json

def get_strategic_sites(lat, lon, radius_km=50):
    """
    Queries Overpass API for military bases and nuclear power plants near a location.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Radius in meters for Overpass
    radius = radius_km * 1000
    
    query = f"""
    [out:json][timeout:25];
    (
      node["military"](around:{radius},{lat},{lon});
      way["military"](around:{radius},{lat},{lon});
      relation["military"](around:{radius},{lat},{lon});
      node["landuse"="military"](around:{radius},{lat},{lon});
      way["landuse"="military"](around:{radius},{lat},{lon});
      relation["landuse"="military"](around:{radius},{lat},{lon});
      node["power"="plant"]["generator:source"="nuclear"](around:{radius},{lat},{lon});
      way["power"="plant"]["generator:source"="nuclear"](around:{radius},{lat},{lon});
      relation["power"="plant"]["generator:source"="nuclear"](around:{radius},{lat},{lon});
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
    sites = get_strategic_sites(besancon_lat, besancon_lon)
    print(json.dumps(sites, indent=2))
