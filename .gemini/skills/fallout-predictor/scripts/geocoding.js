const cityName = process.argv[2];

if (!cityName) {
  console.error('Usage: node geocoding.js <city_name>');
  process.exit(1);
}

async function getCoordinates(city) {
  try {
    const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.results && data.results.length > 0) {
      const result = data.results[0];
      console.log(JSON.stringify({
        name: result.name,
        latitude: result.latitude,
        longitude: result.longitude,
        country: result.country,
        admin1: result.admin1
      }, null, 2));
    } else {
      console.error(`No results found for city: ${city}`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`Error fetching coordinates: ${error.message}`);
    process.exit(1);
  }
}

getCoordinates(cityName);
