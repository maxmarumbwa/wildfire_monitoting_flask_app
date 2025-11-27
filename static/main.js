document.addEventListener('DOMContentLoaded', async () => {
  // Initialize map first
  const map = L.map('map').setView([-19.1, 29.8], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }).addTo(map);

  // Create layer groups
  const fireHotspotsLayer = L.layerGroup().addTo(map);
  const polygonsLayer = L.layerGroup().addTo(map);

  // Create layer control
  const baseLayers = {
    "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }),
  openTopoMap: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)'
})
  };

  const overlayLayers = {
    "Fire Hotspots": fireHotspotsLayer,
    "Administrative Boundaries": polygonsLayer
  };

  L.control.layers(baseLayers, overlayLayers).addTo(map);

  // Then load data with the layer groups
  await loadFireData(fireHotspotsLayer);
  await loadPolygons(polygonsLayer);
});

// Load fire hotspot data
async function loadFireData(layerGroup) {
  const res = await fetch('/api/fire_hotspots');
  const data = await res.json();
 
  data.features.forEach(f => {
    const [lon, lat] = f.geometry.coordinates;
    const properties = f.properties || {};
    
    // Create popup content with fire information
    const popupContent = createFirePopupContent(properties);
    
    // Create circle marker with click event
    L.circleMarker([lat, lon], {
      radius: 5,
      color: 'red',
      fillColor: '#f03',
      fillOpacity: 0.8,
      weight: 1
    })
    .bindPopup(popupContent)
    .on('click', function(e) {
      // Optional: You can add additional click handling here
      console.log('Fire hotspot clicked:', properties);
    })
    .addTo(layerGroup);
  });
}

// Create popup content for fire hotspots
function createFirePopupContent(properties) {
  // Customize this based on what data your API returns
  let content = '<div class="fire-popup"><h3>🔥 Fire Hotspot</h3>';
  
  // Add common fire hotspot properties
  if (properties.confidence) {
    content += `<p><strong>Confidence:</strong> ${properties.confidence}%</p>`;
  }
  
  if (properties.brightness) {
    content += `<p><strong>Brightness:</strong> ${properties.brightness}°C</p>`;
  }
  
  if (properties.acq_date) {
    content += `<p><strong>Date:</strong> ${formatDate(properties.acq_date)}</p>`;
  }
  
  if (properties.acq_time) {
    content += `<p><strong>Time:</strong> ${formatTime(properties.acq_time)}</p>`;
  }
  
  if (properties.satellite) {
    content += `<p><strong>Satellite:</strong> ${properties.satellite}</p>`;
  }
  
  if (properties.frp) {
    content += `<p><strong>Fire Radiative Power:</strong> ${properties.frp} MW</p>`;
  }
  
  // Add any other properties that might be useful
  Object.keys(properties).forEach(key => {
    if (!['confidence', 'brightness', 'acq_date', 'acq_time', 'satellite', 'frp'].includes(key)) {
      content += `<p><strong>${key}:</strong> ${properties[key]}</p>`;
    }
  });
  
  content += '</div>';
  return content;
}

// Helper function to format date
function formatDate(dateString) {
  try {
    return new Date(dateString).toLocaleDateString();
  } catch (e) {
    return dateString;
  }
}

// Helper function to format time
function formatTime(timeString) {
  if (!timeString) return 'Unknown';
  
  // If time is in HHMM format (common in fire data)
  if (timeString.length === 4) {
    const hours = timeString.substring(0, 2);
    const minutes = timeString.substring(2, 4);
    return `${hours}:${minutes}`;
  }
  
  return timeString;
}

// Load baseline polygon data
async function loadPolygons(layerGroup) {
  const res = await fetch('/api/admin1');
  const data = await res.json();

  L.geoJSON(data, {
    style: { 
      color: 'blue', 
      weight: 1, 
      fillOpacity: 0.1,
      fillColor: 'lightblue'
    },
    onEachFeature: function(feature, layer) {
      if (feature.properties && feature.properties.ADM1_EN) {
        layer.bindPopup(feature.properties.ADM1_EN);
      }
    }
  }).addTo(layerGroup);
}

