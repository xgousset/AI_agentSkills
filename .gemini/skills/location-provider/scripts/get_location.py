import requests
import json

def get_location():
    """
    Retrieves geolocation data based on the public IP address.
    Uses multiple fallback services.
    """
    services = [
        {"url": "http://ip-api.com/json/", "parser": lambda d: {
            "lat": d.get('lat'), "lon": d.get('lon'), "city": d.get('city'), "status": d.get('status') == 'success'
        }},
        {"url": "https://ipapi.co/json/", "parser": lambda d: {
            "lat": d.get('latitude'), "lon": d.get('longitude'), "city": d.get('city'), "status": 'latitude' in d
        }}
    ]
    
    for service in services:
        try:
            response = requests.get(service['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                loc = service['parser'](data)
                if loc['status']:
                    return loc
        except:
            continue
            
    return {"error": "All geolocation services failed"}

if __name__ == "__main__":
    location = get_location()
    print(json.dumps(location, indent=2))
