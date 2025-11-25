document.addEventListener('DOMContentLoaded', async () => {
  // Initialize map first
  const map = L.map('map').setView([-19.1, 29.8], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
  
  // Then load polygons with the map instance
  await loadFireData(map);
});


//Load fire hotspot data
async function loadFireData(map) {
  const res = await fetch('/api/fire_hotspots');
  const data = await res.json();
 
  data.features.forEach(f => {
    const [lon, lat] = f.geometry.coordinates;
    L.circleMarker([lat, lon], {radius:1}).addTo(map);
  });
}

//Load polygon data
async function loadPolygons(map) {
  const res = await fetch('/api/admin1');
  const data = await res.json();

  L.geoJSON(data, {
    style: { color: 'blue', weight: 1, fillOpacity: 0.2 },
    onEachFeature: function(feature, layer) {
      if (feature.properties && feature.properties.ADM1_EN) {
        layer.bindPopup(feature.properties.ADM1_EN);
      }
    }
  }).addTo(map);
}
