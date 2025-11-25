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
    L.circleMarker([lat, lon], {
      radius: 1,
      color: 'red',
      fillColor: '#f03',
      fillOpacity: 0.8
    }).addTo(layerGroup);
  });
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