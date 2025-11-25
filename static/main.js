document.addEventListener('DOMContentLoaded', async () => {
  const map = L.map('map').setView([-19.1, 29.8], 6);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

  const res = await fetch('/api/fire_hotspots');
  const data = await res.json();

  data.features.forEach(f => {
    const [lon, lat] = f.geometry.coordinates;
    L.circleMarker([lat, lon], {radius:3}).addTo(map);
  });
});
