// Demo GPS Navigator - Modern UI JavaScript

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
            showToast('Please load a map first!', 'warning');
            return;
        }
        
        if (!startCoords) {
            setStartPoint(e.latlng.lat, e.latlng.lng);
        } else if (!endCoords) {
            setEndPoint(e.latlng.lat, e.latlng.lng);
        } else {
            showToast('Clear the route to set new points', 'info');
        }
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#10B981' : type === 'warning' ? '#F59E0B' : '#4F46E5'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

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
        <div class="status-badge status-badge-info w-100 justify-content-center">
            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
            <span>Loading map...</span>
        </div>
    `;
    loadBtn.disabled = true;
    loadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
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
            showToast('Map loaded successfully!', 'success');
            
            // Update stats with modern KPI layout
            document.getElementById('mapStats').style.display = 'block';
            document.getElementById('statNodes').textContent = data.stats.num_nodes.toLocaleString();
            document.getElementById('statEdges').textContent = data.stats.num_edges.toLocaleString();
            document.getElementById('dataSource').textContent = data.stats.data_source;
            
            // Center map
            if (data.bounds) {
                map.setView(data.bounds.center, 14);
            }
            
            statusDiv.innerHTML = '';
        } else {
            throw new Error(data.error || 'Failed to load map');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error loading map: ' + error.message, 'warning');
        statusDiv.innerHTML = `
            <div class="status-badge status-badge-info w-100 justify-content-center" style="background: #FEE2E2; color: #991B1B; border-color: #FECACA;">
                <i class="fas fa-exclamation-circle"></i>
                <span>Failed to load</span>
            </div>
        `;
    } finally {
        loadBtn.disabled = false;
        loadBtn.innerHTML = '<i class="fas fa-download me-2"></i>Load Map';
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
    
    // Draw route with modern styling
    const coordinates = route.coordinates.map(c => [c[0], c[1]]);
    routeLayer = L.polyline(coordinates, {
        color: '#4F46E5',
        weight: 6,
        opacity: 0.8,
        lineJoin: 'round'
    }).addTo(map);
    
    // Fit map to route
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
    
    // Display modern route summary
    const routeInfoDiv = document.getElementById('routeInfo');
    routeInfoDiv.innerHTML = `
        <div class="kpi-container mb-3">
            <div class="kpi-card">
                <div class="kpi-icon">
                    <i class="fas fa-route"></i>
                </div>
                <div class="kpi-label">Distance</div>
                <div class="kpi-value" style="font-size: 1.5rem;">${route.distance_km.toFixed(2)}</div>
                <div class="step-distance">kilometers</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="kpi-label">ETA</div>
                <div class="kpi-value" style="font-size: 1.5rem;">${Math.round(route.travel_time_minutes)}</div>
                <div class="step-distance">minutes</div>
            </div>
        </div>
        <div class="status-badge status-badge-success w-100 justify-content-center">
            <i class="fas fa-check-circle"></i>
            <span>Optimal Route Found</span>
        </div>
    `;
    
    // Show algorithm stats with fade-in animation
    const algoStatsDiv = document.getElementById('algoStats');
    const algoStatsEmpty = document.getElementById('algoStatsEmpty');
    
    if (algoStatsEmpty) algoStatsEmpty.style.display = 'none';
    algoStatsDiv.style.display = 'block';
    algoStatsDiv.classList.add('fade-in');
    
    document.getElementById('nodesExplored').textContent = route.nodes_explored.toLocaleString();
    document.getElementById('pathLength').textContent = route.path.length;
    
    // Show modern turn-by-turn directions
    let directionsHTML = '<div class="directions-list">';
    route.turn_by_turn.forEach((step, i) => {
        if (i < 15) {  // Show first 15 steps
            directionsHTML += `
                <div class="direction-step">
                    <div class="step-icon">
                        <i class="fas fa-arrow-right"></i>
                    </div>
                    <div class="step-content">
                        <div class="step-instruction">${step.instruction}</div>
                        <div class="step-distance">${(step.distance / 1000).toFixed(2)} km</div>
                    </div>
                </div>
            `;
        }
    });
    if (route.turn_by_turn.length > 15) {
        directionsHTML += `
            <div class="direction-step" style="opacity: 0.6;">
                <div class="step-icon">
                    <i class="fas fa-ellipsis-h"></i>
                </div>
                <div class="step-content">
                    <div class="step-instruction">and ${route.turn_by_turn.length - 15} more steps...</div>
                </div>
            </div>
        `;
    }
    directionsHTML += '</div>';
    document.getElementById('directions').innerHTML = directionsHTML;
    
    showToast('Route calculated successfully!', 'success');
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
    
    // Reset UI to empty states
    document.getElementById('routeInfo').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-route"></i>
            <p class="mb-0">No route calculated</p>
        </div>
    `;
    
    document.getElementById('algoStats').style.display = 'none';
    if (document.getElementById('algoStatsEmpty')) {
        document.getElementById('algoStatsEmpty').style.display = 'block';
    }
    
    document.getElementById('directions').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-directions"></i>
            <p class="mb-0" style="font-size: 0.875rem;">Directions will appear here</p>
        </div>
    `;
    
    showToast('Route cleared', 'info');
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
