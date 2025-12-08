// static/js/map-utils.js

function createMap(divId, geojsonUrl) {

    const map = L.map(divId).setView([-17, 30], 6);

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        { maxZoom: 18 }
    ).addTo(map);

    fetch(geojsonUrl)
        .then(res => res.json())
        .then(data => {
            const layer = L.geoJSON(data, {
                pointToLayer: (feature, latlng) =>
                    L.circleMarker(latlng, {
                        radius: 5,
                        fillColor: "red",
                        color: "#000",
                        weight: 1,
                        fillOpacity: 0.8
                    })
            }).addTo(map);

            if (layer.getBounds().isValid()) {
                map.fitBounds(layer.getBounds());
            }
        })
        .catch(err => console.error("Map error:", err));
}

// 🔑 make it globally accessible
window.createMap = createMap;
