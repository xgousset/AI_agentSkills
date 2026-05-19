import csv
import math
import os

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_closest_nuclear_plants(lat, lon, limit=5):
    csv_path = ".gemini/skills/risk-analyst/assets/nuclear_plants.csv"
    if not os.path.exists(csv_path):
        return {"error": "Local database not found"}
        
    plants = []
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                # Based on GPPD v1.3 format:
                # 1: country_long, 2: name, 4: capacity_mw, 5: latitude, 6: longitude
                p_lat = float(row[5])
                p_lon = float(row[6])
                dist = calculate_distance(lat, lon, p_lat, p_lon)
                plants.append({
                    "name": row[2],
                    "country": row[1],
                    "distance_km": round(dist, 1),
                    "capacity_mw": row[4]
                })
            except:
                continue
                
    return sorted(plants, key=lambda x: x['distance_km'])[:limit]

if __name__ == "__main__":
    # Test for Besançon
    print(get_closest_nuclear_plants(47.24, 6.02))
