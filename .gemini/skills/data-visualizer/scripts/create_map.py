import matplotlib.pyplot as plt
import numpy as np

def generate_blast_map(lat, lon, yield_kt, output_path="blast_map.png"):
    """
    Generates a simple visualization of blast radii.
    """
    # Simple calculation for radii (in km) - very rough approximation
    thermal_radius = 1.5 * (yield_kt / 12)**0.5
    blast_radius = 2.5 * (yield_kt / 12)**0.33
    radiation_radius = 0.8 * (yield_kt / 12)**0.5

    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Circles for radii
    circle_thermal = plt.Circle((lon, lat), thermal_radius / 111, color='orange', alpha=0.3, label='Thermal Radiation')
    circle_blast = plt.Circle((lon, lat), blast_radius / 111, color='red', alpha=0.2, label='Blast Wave (Moderate)')
    circle_rad = plt.Circle((lon, lat), radiation_radius / 111, color='blue', alpha=0.4, label='Prompt Radiation')
    
    ax.add_patch(circle_blast)
    ax.add_patch(circle_thermal)
    ax.add_patch(circle_rad)
    
    ax.plot(lon, lat, 'k*', markersize=15, label='Ground Zero')
    
    ax.set_aspect('equal')
    ax.set_title(f"Impact Visualization: {yield_kt}kt Detonation")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend()
    ax.grid(True)
    
    # Set limits slightly outside the largest circle
    limit = max(thermal_radius, blast_radius) / 111 * 1.5
    ax.set_xlim(lon - limit, lon + limit)
    ax.set_ylim(lat - limit, lat + limit)
    
    plt.savefig(output_path, dpi=100)
    plt.close()
    print(f"Blast map generated at: {output_path}")

if __name__ == "__main__":
    # Test for Besancon
    generate_blast_map(47.2455, 6.0209, 12)
