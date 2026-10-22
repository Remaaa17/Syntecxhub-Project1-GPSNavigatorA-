// Demo GPS Navigator - Simple JavaScript for demo version

let map;
let routeLayer;
let startMarker;
let endMarker;
let mapLoaded = false;
let startCoords = null;
let endCoords = null;
let currentRoute = null;

// Initialize map
function initMap() {
    map = L.map('map').setView([30.0444, 31.2357], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add click handler
    map.on('click', function(e) {
        if (!mapLoaded) {
            alert('Please generate the sample city first!');
            return;
        }
        
        if (!startCoords) {
            setStartPoint(e.latlng.lat, e.latlng.lng);
        } else if (!endCoords) {
            setEndPoint(e.latlng.lat, e.latlng.lng);
        } else {
            alert('Clear the route to set new points');
        }
    });
}

// Set start point
function setStartPoint(lat, lng) {
    startCoords = { lat, lng };
    
    if (startMarker) {
        map.removeLayer(startMarker);
    }
    
    startMarker = L.marker([lat, lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    startMarker.bindPopup('<b>Start Point</b>').openPopup();
    console.log('Start point set:', lat, lng);
}

// Set end point
function setEndPoint(lat, lng) {
    endCoords = { lat, lng };
    
    if (endMarker) {
        map.removeLayer(endMarker);
    }
    
    endMarker = L.marker([lat, lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    endMarker.bindPopup('<b>End Point</b>').openPopup();
    console.log('End point set:', lat, lng);
    
    // Fit map to both markers
    if (startMarker && endMarker) {
        const group = L.featureGroup([startMarker, endMarker]);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Load map
async function loadMap() {
    const statusDiv = document.getElementById('mapStatus');
    const loadBtn = document.getElementById('loadMapBtn');
    const citySelect = document.getElementById('citySelect');
    
    const selectedCity = citySelect.value;
    const selectedOption = citySelect.options[citySelect.selectedIndex];
    const useRealData = selectedOption.dataset.real === 'true';
    
    statusDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="spinner-border spinner-border-sm me-2"></div>
            ${useRealData ? 'Downloading real map data...' : 'Generating sample data...'}
        </div>
    `;
    loadBtn.disabled = true;
    
    try {
        const response = await fetch('/api/load_map', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                place_name: selectedCity,
                use_real_data: useRealData
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mapLoaded = true;
            
            // Update map view
            map.setView(data.bounds.center, 13);
            
            // Show success
            const dataType = data.stats.data_source.includes('real') ? 'REAL' : 'SAMPLE';
            statusDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>✓ Map loaded!</strong><br>
                    <small>${data.message}</small>
                </div>
            `;
            
            // Update stats
            document.getElementById('mapStats').style.display = 'block';
            document.getElementById('dataSource').innerHTML = `
                <i class="fas fa-${useRealData ? 'globe' : 'dice'} me-2"></i>
                ${data.stats.data_source}
            `;
            document.getElementById('statNodes').textContent = data.stats.num_nodes.toLocaleString();
            document.getElementById('statEdges').textContent = data.stats.num_edges.toLocaleString();
            
            console.log('Map loaded:', data.stats);
        } else {
            statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-danger">
                Error: ${error.message}<br>
                <small>Check console for details</small>
            </div>
        `;
        console.error('Error loading map:', error);
    } finally {
        loadBtn.disabled = false;
    }
}

// Find route
async function findRoute() {
    if (!mapLoaded) {
        alert('Please generate the sample city first!');
        return;
    }
    
    if (!startCoords || !endCoords) {
        alert('Please set both start and end points by clicking on the map!');
        return;
    }
    
    const routeType = document.getElementById('routeType').value;
    const routeInfoDiv = document.getElementById('routeInfo');
    
    routeInfoDiv.innerHTML = '<div class="text-center"><div class="spinner-border"></div><p>Calculating route...</p></div>';
    
    try {
        const response = await fetch('/api/find_route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_lat: startCoords.lat,
                start_lon: startCoords.lng,
                end_lat: endCoords.lat,
                end_lon: endCoords.lng,
                route_type: routeType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayRoute(data.route);
            console.log('Route found:', data.route);
        } else {
            const errorMsg = data.suggestion ? 
                `${data.error}<br><small class="text-muted">${data.suggestion}</small>` :
                data.error;
            routeInfoDiv.innerHTML = `
                <div class="alert alert-warning">
                    <h6><i class="fas fa-exclamation-triangle"></i> ${data.error}</h6>
                    ${data.suggestion ? `<p class="mb-0"><small>${data.suggestion}</small></p>` : ''}
                    <hr>
                    <small><strong>Tip:</strong> Try clicking points that are closer together, preferably on the same street or neighborhood.</small>
                </div>
            `;
        }
    } catch (error) {
        routeInfoDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
        console.error('Error finding route:', error);
    }
}

// Display route
function displayRoute(route) {
    // Store current route
    currentRoute = route;
    
    // Remove existing route
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    
    // Draw route
    const coordinates = route.coordinates.map(c => [c[0], c[1]]);
    routeLayer = L.polyline(coordinates, {
        color: '#007bff',
        weight: 5,
        opacity: 0.7
    }).addTo(map);
    
    // Fit map to route
    map.fitBounds(routeLayer.getBounds());
    
    // Display info
    const routeInfoDiv = document.getElementById('routeInfo');
    routeInfoDiv.innerHTML = `
        <div class="alert alert-success">
            <h6>✓ Route Found!</h6>
        </div>
        <div class="mb-2">
            <strong>Type:</strong> ${route.type}
        </div>
        <div class="mb-2">
            <strong>Distance:</strong> ${route.distance_km.toFixed(2)} km
        </div>
        <div class="mb-2">
            <strong>Travel Time:</strong> ${route.travel_time_minutes.toFixed(1)} minutes
        </div>
        <div class="mb-2">
            <strong>Path Length:</strong> ${route.path.length} nodes
        </div>
    `;
    
    // Show algorithm stats
    document.getElementById('algoStats').style.display = 'block';
    document.getElementById('nodesExplored').textContent = route.nodes_explored.toLocaleString();
    document.getElementById('pathLength').textContent = route.path.length;
    
    // Show directions
    let directionsHTML = '<h6>Turn-by-Turn Directions:</h6><ol>';
    route.turn_by_turn.forEach((step, i) => {
        if (i < 10) {  // Show first 10 steps
            directionsHTML += `<li>${step.instruction}</li>`;
        }
    });
    if (route.turn_by_turn.length > 10) {
        directionsHTML += `<li><em>... and ${route.turn_by_turn.length - 10} more steps</em></li>`;
    }
    directionsHTML += '</ol>';
    document.getElementById('directions').innerHTML = directionsHTML;
}

// Clear route
function clearRoute() {
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    if (startMarker) {
        map.removeLayer(startMarker);
    }
    if (endMarker) {
        map.removeLayer(endMarker);
    }
    
    startCoords = null;
    endCoords = null;
    currentRoute = null;
    
    document.getElementById('routeInfo').innerHTML = `
        <div class="text-center text-muted py-4">
            <i class="fas fa-route fa-3x mb-3 opacity-25"></i>
            <p>No route calculated yet</p>
        </div>
    `;
    
    document.getElementById('algoStats').style.display = 'none';
    document.getElementById('directions').innerHTML = '<p class="text-muted">Route directions will appear here</p>';
    
    console.log('Route cleared');
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('Demo GPS Navigator loaded!');
    
    initMap();
    
    document.getElementById('loadMapBtn').addEventListener('click', loadMap);
    document.getElementById('findRouteBtn').addEventListener('click', findRoute);
    document.getElementById('clearRouteBtn').addEventListener('click', clearRoute);
    
    console.log('Event listeners attached. Click "Load Map" to start!');
});
