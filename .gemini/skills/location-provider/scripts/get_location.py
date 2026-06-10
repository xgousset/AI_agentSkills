import requests
import json

def get_location():
    """
    Retrieves geolocation data based on the public IP address.
    Uses multiple fallback services.
    """
    # Prefer HTTP for ip-api as SSL requires a key
    services = [
        {"url": "http://ip-api.com/json/", "parser": lambda d: {
            "lat": d.get('lat'), "lon": d.get('lon'), "city": d.get('city'), "status": d.get('status') == 'success'
        }},
        {"url": "https://ipapi.co/json/", "parser": lambda d: {
            "lat": d.get('latitude'), "lon": d.get('longitude'), "city": d.get('city'), "status": 'latitude' in d
        }},
        {"url": "https://ipinfo.io/json", "parser": lambda d: {
            "lat": float(d.get('loc', '0,0').split(',')[0]), 
            "lon": float(d.get('loc', '0,0').split(',')[1]), 
            "city": d.get('city'), 
            "status": 'loc' in d
        }}
    ]
    
    for service in services:
        try:
            # Add a user-agent to avoid being blocked by some services (like Cloudflare on ipapi.co)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(service['url'], headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                loc = service['parser'](data)
                if loc['status']:
                    return loc
        except Exception as e:
            continue
            
    return {"error": "All geolocation services failed"}

if __name__ == "__main__":
    location = get_location()
    print(json.dumps(location, indent=2))
