const fs = require('fs');
const path = require('path');

const lat = process.argv[2];
const lon = process.argv[3];
const zoom = process.argv[4] || 12;
const width = process.argv[5] || 800;
const height = process.argv[6] || 600;

if (!lat || !lon) {
  console.error('Usage: node get_map.js <lat> <lon> [zoom] [width] [height]');
  process.exit(1);
}

async function downloadMap(lat, lon, zoom, width, height) {
  // Use Yandex Static Maps API - often permissive without key for low volume
  const url = `https://static-maps.yandex.ru/1.x/?ll=${lon},${lat}&z=${zoom}&size=${width},${height}&l=map&pt=${lon},${lat},pm2rdm`;
  const filename = `map_${lat}_${lon}.png`;
  const filePath = path.join(process.cwd(), '.gemini', 'skills', 'fallout-predictor', 'assets', filename);

  // Ensure assets directory exists
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  try {
    console.log(`Fetching map from: ${url}`);
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'GeminiFalloutPredictor/1.0 (contact@example.com)'
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    fs.writeFileSync(filePath, buffer);
    
    console.log(JSON.stringify({
      status: 'success',
      path: filePath,
      attribution: '© OpenStreetMap contributors'
    }, null, 2));
  } catch (error) {
    console.error(`Error downloading map: ${error.message}`);
    process.exit(1);
  }
}

downloadMap(lat, lon, zoom, width, height);
