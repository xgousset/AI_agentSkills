import requests
import json

def get_location():
    """
    Retrieves geolocation data based on the public IP address.
    Uses ip-api.com (free tier, no key required).
    """
    try:
        # IP-API (JSON format)
        url = "http://ip-api.com/json/"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                location_info = {
                    "lat": data.get('lat'),
                    "lon": data.get('lon'),
                    "city": data.get('city'),
                    "region": data.get('regionName'),
                    "country": data.get('country'),
                    "ip": data.get('query'),
                    "isp": data.get('isp')
                }
                return location_info
            else:
                return {"error": f"Geolocation failed: {data.get('message')}"}
        else:
            return {"error": f"HTTP Error: {response.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    location = get_location()
    print(json.dumps(location, indent=2))
