import requests
import json
import os
import tempfile
import time

CACHE_FILE = os.path.join(tempfile.gettempdir(), "fallout_weather_cache.json")
CACHE_EXPIRY = 900 # 15 minutes

def get_wind_data(lat, lon):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
            if time.time() - cache['timestamp'] < CACHE_EXPIRY:
                return cache['data']

    # Open-Meteo API with high-resolution vertical wind profile
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=wind_speed_10m,wind_direction_10m&hourly=wind_speed_10m,wind_speed_80m,wind_speed_120m,wind_speed_180m,wind_direction_10m,wind_direction_80m,wind_direction_120m,wind_direction_180m,pressure_msl&models=best_match"
    
    # Implementation uses standard requests for now, but structured for parallel execution if moved to a sub-agent
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current_wind = {
            "surface": {"speed": data['current']['wind_speed_10m'], "direction": data['current']['wind_direction_10m']},
            "layers": [
                {"alt": "80m", "speed": data['hourly']['wind_speed_80m'][0], "direction": data['hourly']['wind_direction_80m'][0]},
                {"alt": "120m", "speed": data['hourly']['wind_speed_120m'][0], "direction": data['hourly']['wind_direction_120m'][0]},
                {"alt": "180m", "speed": data['hourly']['wind_speed_180m'][0], "direction": data['hourly']['wind_direction_180m'][0]}
            ],
            "units": data['current_units']
        }
        
        with open(CACHE_FILE, 'w') as f:
            json.dump({"timestamp": time.time(), "data": current_wind}, f)
            
        return current_wind
    else:
        return {"error": f"Weather API error: {response.status_code}"}

if __name__ == "__main__":
    # Example: Besançon coordinates
    besancon_lat, besancon_lon = 47.2378, 6.0244
    wind = get_wind_data(besancon_lat, besancon_lon)
    print(json.dumps(wind, indent=2))
