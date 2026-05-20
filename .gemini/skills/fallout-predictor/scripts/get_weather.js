const lat = process.argv[2];
const lon = process.argv[3];

if (!lat || !lon) {
  console.error('Usage: node get_weather.js <lat> <lon>');
  process.exit(1);
}

async function getWeather(lat, lon) {
  try {
    // Open-Meteo API for wind speed/direction at multiple altitudes
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=wind_speed_10m,wind_direction_10m&hourly=wind_speed_80m,wind_direction_80m,wind_speed_120m,wind_direction_120m,wind_speed_180m,wind_direction_180m&wind_speed_unit=kmh`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    
    const data = await response.json();
    
    const result = {
      surface: {
        speed: data.current.wind_speed_10m,
        direction: data.current.wind_direction_10m
      },
      altitude_low: { // ~180m
        speed: data.hourly.wind_speed_180m[0],
        direction: data.hourly.wind_direction_180m[0]
      }
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(`Error fetching weather: ${error.message}`);
    process.exit(1);
  }
}

getWeather(lat, lon);
