// GPS Navigator - Enhanced Map and Interaction Logic

let map;
let routeLayer;
let startMarker;
let endMarker;
let mapLoaded = false;
let startCoords = null;
let endCoords = null;
let currentRouteData = null;

// Toast notification helper
function showToast(message, type = 'success') {
    const toastId = type === 'success' ? 'successToast' : 'errorToast';
    const messageId = type === 'success' ? 'successMessage' : 'errorMessage';
    
    document.getElementById(messageId).textContent = message;
    const toast = new bootstrap.Toast(document.getElementById(toastId));
    toast.show();
}

// Update system status
function updateStatus(status, color = 'success') {
    const statusIndicator = document.getElementById('systemStatus');
    const colorClass = color === 'success' ? 'text-success' : 
                       color === 'warning' ? 'text-warning' : 
                       color === 'danger' ? 'text-danger' : 'text-info';
    
    statusIndicator.innerHTML = `
        <i class="fas fa-circle ${colorClass} pulse"></i>
        <span class="small">${status}</span>
    `;
}

// Initialize map with enhanced controls
function initMap() {
    map = L.map('map', {
        zoomControl: false  // We'll add custom controls
    }).setView([37.8267, -122.2233], 13);
    
    // Add OpenStreetMap tiles with better styling
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Add click handler for setting start/end points
    map.on('click', function(e) {
        if (!mapLoaded) {
            showToast('Please load a map first!', 'error');
            return;
        }
        
        if (!startCoords) {
            setStartPoint(e.latlng.lat, e.latlng.lng);
            hideMapInstructions();
            showToast('Start point set! Click again for end point.', 'success');
        } else if (!endCoords) {
            setEndPoint(e.latlng.lat, e.latlng.lng);
            showToast('End point set! Click "Find Route" to calculate.', 'success');
        } else {
            showToast('Clear the route to set new points', 'error');
        }
    });
    
    updateStatus('Ready to load map', 'info');
}

// Hide map instructions
function hideMapInstructions() {
    const instructions = document.getElementById('mapInstructions');
    if (instructions) {
        instructions.style.display = 'none';
    }
}

// Show loading overlay
function showLoadingOverlay(show = true) {
    document.getElementById('mapLoadingOverlay').style.display = show ? 'flex' : 'none';
}

// Set start point with animation
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
    
    startMarker.bindPopup('<b>Start Point</b><br>Click the map for end point').openPopup();
    document.getElementById('startAddress').value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    
    // Animate map to marker
    map.panTo([lat, lng]);
}

// Set end point with animation
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
    
    endMarker.bindPopup('<b>End Point</b><br>Ready to find route!').openPopup();
    document.getElementById('endAddress').value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    
    // Fit map to both markers
    if (startMarker && endMarker) {
        const group = L.featureGroup([startMarker, endMarker]);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Load map data with enhanced UI feedback
async function loadMap() {
    const place = document.getElementById('placeInput').value;
    const statusDiv = document.getElementById('mapStatus');
    const loadBtn = document.getElementById('loadMapBtn');
    
    statusDiv.innerHTML = `
        <div class="alert alert-info animate__animated animate__fadeIn">
            <div class="spinner-border spinner-border-sm me-2"></div>
            Loading map data...This may take a moment.
        </div>
    `;
    loadBtn.disabled = true;
    loadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    updateStatus('Loading map...', 'warning');
    
    try {
        const response = await fetch('/api/load_map', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ place_name: place })
        });
        
        const data = await response.json();
        
        if (data.success) {
            mapLoaded = true;
            
            // Update map view
            const bounds = data.bounds;
            map.setView(bounds.center, 13);
            
            // Show success message
            statusDiv.innerHTML = `
                <div class="alert alert-success animate__animated animate__fadeIn">
                    <i class="fas fa-check-circle me-2"></i>
                    <strong>Map Loaded Successfully!</strong>
                </div>
            `;
            
            // Update map stats
            document.getElementById('mapStats').style.display = 'block';
            document.getElementById('statNodes').textContent = data.stats.num_nodes.toLocaleString();
            document.getElementById('statEdges').textContent = data.stats.num_edges.toLocaleString();
            document.getElementById('statLength').textContent = data.stats.total_length_km.toFixed(1);
            
            showToast(`Map loaded for ${place}!`, 'success');
            updateStatus('Map loaded - Ready!', 'success');
            
        } else {
            statusDiv.innerHTML = `
                <div class="alert alert-danger animate__animated animate__shakeX">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error: ${data.error}
                </div>
            `;
            showToast('Failed to load map', 'error');
            updateStatus('Error loading map', 'danger');
        }
    } catch (error) {
        statusDiv.innerHTML = `
            <div class="alert alert-danger animate__animated animate__shakeX">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error: ${error.message}
            </div>
        `;
        showToast('Network error', 'error');
        updateStatus('Connection error', 'danger');
    } finally {
        loadBtn.disabled = false;
        loadBtn.innerHTML = '<i class="fas fa-download me-2"></i>Load Map';
    }
}

// Geocode address with enhanced feedback
async function geocodeAddress(address, isStart) {
    if (!address.trim()) {
        showToast('Please enter an address', 'error');
        return;
    }
    
    updateStatus('Searching address...', 'info');
    
    try {
        const response = await fetch('/api/geocode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (isStart) {
                setStartPoint(data.node_lat, data.node_lon);
                showToast('Start address found!', 'success');
            } else {
                setEndPoint(data.node_lat, data.node_lon);
                showToast('End address found!', 'success');
            }
            updateStatus('Address located', 'success');
        } else {
            showToast('Address not found: ' + data.error, 'error');
            updateStatus('Address not found', 'danger');
        }
    } catch (error) {
        showToast('Error geocoding address: ' + error.message, 'error');
        updateStatus('Geocoding error', 'danger');
    }
}

// Find route with enhanced loading and feedback
async function findRoute() {
    if (!mapLoaded) {
        showToast('Please load a map first!', 'error');
        return;
    }
    
    if (!startCoords || !endCoords) {
        showToast('Please set both start and end points!', 'error');
        return;
    }
    
    const routeType = document.getElementById('routeType').value;
    const trafficCondition = document.getElementById('trafficCondition').value;
    
    const routeInfoDiv = document.getElementById('routeInfo');
    const startTime = Date.now();
    
    // Show loading
    showLoadingOverlay(true);
    routeInfoDiv.innerHTML = `
        <div class="text-center py-4 animate__animated animate__pulse animate__infinite">
            <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div>
            <h6>Calculating optimal route...</h6>
            <small class="text-muted">Running A* algorithm</small>
        </div>
    `;
    updateStatus('Calculating route...', 'warning');
    
    try {
        const response = await fetch('/api/find_route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_lat: startCoords.lat,
                start_lon: startCoords.lng,
                end_lat: endCoords.lat,
                end_lon: endCoords.lng,
                route_type: routeType,
                traffic_condition: trafficCondition
            })
        });
        
        const data = await response.json();
        const computeTime = Date.now() - startTime;
        
        if (data.success) {
            if (routeType === 'all') {
                displayMultipleRoutes(data.routes, data.comparison);
                showToast(`Found ${data.routes.length} route options!`, 'success');
            } else {
                displayRoute(data.route, computeTime);
                showToast('Route calculated successfully!', 'success');
            }
            updateStatus('Route found!', 'success');
        } else {
            routeInfoDiv.innerHTML = `
                <div class="alert alert-danger animate__animated animate__shakeX">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No route found!
                </div>
            `;
            showToast('No route found!', 'error');
            updateStatus('No route available', 'danger');
        }
    } catch (error) {
        routeInfoDiv.innerHTML = `
            <div class="alert alert-danger animate__animated animate__shakeX">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error: ${error.message}
            </div>
        `;
        showToast('Error calculating route', 'error');
        updateStatus('Calculation error', 'danger');
    } finally {
        showLoadingOverlay(false);
    }
}

// Display single route with enhanced visuals
function displayRoute(route, computeTime = 0) {
    currentRouteData = route;
    
    // Remove existing route
    if (routeLayer) {
        map.removeLayer(routeLayer);
    }
    
    // Draw route on map with animation
    const coordinates = route.coordinates.map(c => [c[0], c[1]]);
    routeLayer = L.polyline(coordinates, {
        color: '#007bff',
        weight: 6,
        opacity: 0.8,
        lineJoin: 'round',
        className: 'animated-route'
    }).addTo(map);
    
    // Fit map to route with animation
    map.flyToBounds(routeLayer.getBounds(), {
        padding: [50, 50],
        duration: 1
    });
    
    // Get route icon
    const routeIcons = {
        'fastest': '⚡',
        'shortest': '📏',
        'no_highways': '🛣️',
        'scenic': '🌳',
        'fuel_efficient': '⛽'
    };
    const icon = routeIcons[route.type] || '🗺️';
    
    // Display route info with enhanced styling
    const routeInfoDiv = document.getElementById('routeInfo');
    routeInfoDiv.innerHTML = `
        <div class="animate__animated animate__fadeIn">
            <div class="text-center mb-3">
                <h2 style="font-size: 3rem;">${icon}</h2>
                <h5 class="text-primary">${route.type.replace('_', ' ').toUpperCase()}</h5>
            </div>
            
            <div class="route-stat animate__animated animate__fadeInUp">
                <div class="d-flex align-items-center">
                    <i class="fas fa-route text-primary me-2"></i>
                    <strong>Distance</strong>
                </div>
                <span>${route.distance_km.toFixed(2)} km</span>
            </div>
            
            <div class="route-stat animate__animated animate__fadeInUp" style="animation-delay: 0.1s;">
                <div class="d-flex align-items-center">
                    <i class="fas fa-clock text-success me-2"></i>
                    <strong>Travel Time</strong>
                </div>
                <span>${route.travel_time_minutes.toFixed(0)} min</span>
            </div>
            
            <div class="route-stat animate__animated animate__fadeInUp" style="animation-delay: 0.2s;">
                <div class="d-flex align-items-center">
                    <i class="fas fa-flag-checkered text-danger me-2"></i>
                    <strong>ETA</strong>
                </div>
                <span>${getETA(route.travel_time_minutes)}</span>
            </div>
            
            <div class="route-stat animate__animated animate__fadeInUp" style="animation-delay: 0.3s;">
                <div class="d-flex align-items-center">
                    <i class="fas fa-tachometer-alt text-info me-2"></i>
                    <strong>Avg Speed</strong>
                </div>
                <span>${((route.distance_km / route.travel_time_minutes) * 60).toFixed(0)} km/h</span>
            </div>
        </div>
    `;
    
    // Show algorithm stats
    if (route.nodes_explored) {
        document.getElementById('algoStats').style.display = 'block';
        document.getElementById('nodesExplored').textContent = route.nodes_explored.toLocaleString();
        document.getElementById('compTime').textContent = computeTime + ' ms';
    }
    
    // Display turn-by-turn directions
    displayDirections(route.turn_by_turn);
    
    // Show print button
    document.getElementById('printDirectionsBtn').style.display = 'block';
}

// Display multiple routes with enhanced comparison
function displayMultipleRoutes(routes, comparison) {
    const comparisonPanel = document.getElementById('comparisonPanel');
    const comparisonContent = document.getElementById('comparisonContent');
    
    comparisonPanel.style.display = 'block';
    
    const routeIcons = {
        'fastest': '⚡',
        'shortest': '📏',
        'no_highways': '🛣️',
        'scenic': '🌳',
        'fuel_efficient': '⛽'
    };
    
    let html = '';
    
    routes.forEach((route, index) => {
        const icon = routeIcons[route.type] || '🗺️';
        const isRecommended = route.type === comparison.fastest_option || route.type === comparison.shortest_option;
        
        html += `
            <div class="col-md-4 col-sm-6">
                <div class="comparison-card" onclick="selectRoute(${index})" data-index="${index}">
                    ${isRecommended ? '<div class="badge bg-success position-absolute top-0 end-0 m-2">Recommended</div>' : ''}
                    <span class="route-icon">${icon}</span>
                    <div class="route-type">${route.type.replace('_', ' ').toUpperCase()}</div>
                    <div class="route-metric">
                        <span class="metric-label"><i class="fas fa-route me-1"></i>Distance</span>
                        <span class="metric-value">${route.distance_km.toFixed(1)} km</span>
                    </div>
                    <div class="route-metric">
                        <span class="metric-label"><i class="fas fa-clock me-1"></i>Time</span>
                        <span class="metric-value">${route.travel_time_minutes.toFixed(0)} min</span>
                    </div>
                    <div class="route-metric">
                        <span class="metric-label"><i class="fas fa-tachometer-alt me-1"></i>Speed</span>
                        <span class="metric-value">${((route.distance_km / route.travel_time_minutes) * 60).toFixed(0)} km/h</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    comparisonContent.innerHTML = html;
    
    // Display first route by default
    if (routes.length > 0) {
        displayRoute(routes[0]);
        document.querySelector('.comparison-card').classList.add('selected');
    }
    
    // Scroll to comparison
    comparisonPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Select route from comparison
function selectRoute(index) {
    const cards = document.querySelectorAll('.comparison-card');
    const route = currentRouteData;
    
    // Get the route data from the API again or store it
    // For now, we'll use a simplified version
    cards.forEach((card, i) => {
        card.classList.toggle('selected', i === index);
    });
    
    showToast(`Route ${index + 1} selected`, 'success');
}

// Display turn-by-turn directions with enhanced styling
function displayDirections(turnByTurn) {
    const directionsDiv = document.getElementById('directions');
    
    if (!turnByTurn || turnByTurn.length === 0) {
        directionsDiv.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-compass fa-3x mb-3 opacity-25"></i>
                <p>No detailed directions available</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="directions-list">';
    
    turnByTurn.forEach((step, index) => {
        const delay = index * 0.05;
        html += `
            <div class="direction-step animate__animated animate__fadeInLeft" 
                 style="animation-delay: ${delay}s;" 
                 data-step="${step.step}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fas fa-location-arrow me-2"></i>
                        <strong>Step ${step.step}:</strong> ${step.instruction}
                    </div>
                    <span class="badge bg-secondary">${step.distance ? step.distance.toFixed(0) + 'm' : ''}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Add summary
    const totalDistance = turnByTurn.reduce((sum, step) => sum + (step.distance || 0), 0);
    html += `
        <div class="alert alert-info mt-3 animate__animated animate__fadeIn">
            <i class="fas fa-info-circle me-2"></i>
            <strong>Total Steps:</strong> ${turnByTurn.length} | 
            <strong>Total Distance:</strong> ${(totalDistance / 1000).toFixed(2)} km
        </div>
    `;
    
    directionsDiv.innerHTML = html;
}

// Calculate ETA
function getETA(minutes) {
    const now = new Date();
    now.setMinutes(now.getMinutes() + minutes);
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// Clear route with animation
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
    currentRouteData = null;
    
    document.getElementById('startAddress').value = '';
    document.getElementById('endAddress').value = '';
    
    document.getElementById('routeInfo').innerHTML = `
        <div class="text-center text-muted py-4 animate__animated animate__fadeIn">
            <i class="fas fa-route fa-3x mb-3 opacity-25"></i>
            <p>No route calculated yet</p>
            <small>Select start and end points to begin</small>
        </div>
    `;
    
    document.getElementById('directions').innerHTML = `
        <div class="text-center text-muted py-4 animate__animated animate__fadeIn">
            <i class="fas fa-compass fa-3x mb-3 opacity-25"></i>
            <p>Directions will appear here after route calculation</p>
        </div>
    `;
    
    // Hide algorithm stats
    document.getElementById('algoStats').style.display = 'none';
    
    // Hide comparison panel
    document.getElementById('comparisonPanel').style.display = 'none';
    
    // Hide print button
    document.getElementById('printDirectionsBtn').style.display = 'none';
    
    showToast('Route cleared', 'success');
    updateStatus('Ready for new route', 'info');
}

// Compare all routes with enhanced UI
async function compareRoutes() {
    if (!mapLoaded) {
        showToast('Please load a map first!', 'error');
        return;
    }
    
    if (!startCoords || !endCoords) {
        showToast('Please set both start and end points!', 'error');
        return;
    }
    
    const routeInfoDiv = document.getElementById('routeInfo');
    showLoadingOverlay(true);
    
    routeInfoDiv.innerHTML = `
        <div class="text-center py-4 animate__animated animate__pulse animate__infinite">
            <div class="spinner-border text-info mb-3" style="width: 3rem; height: 3rem;"></div>
            <h6>Comparing all route options...</h6>
            <small class="text-muted">This may take a moment</small>
        </div>
    `;
    
    updateStatus('Comparing routes...', 'warning');
    
    try {
        const response = await fetch('/api/compare_routes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start_lat: startCoords.lat,
                start_lon: startCoords.lng,
                end_lat: endCoords.lat,
                end_lon: endCoords.lng
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayMultipleRoutes(data.routes, data.comparison);
            showToast(`Successfully compared ${data.routes.length} routes!`, 'success');
            updateStatus('Routes compared', 'success');
        } else {
            routeInfoDiv.innerHTML = `
                <div class="alert alert-danger animate__animated animate__shakeX">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error: ${data.error}
                </div>
            `;
            showToast('Error comparing routes', 'error');
            updateStatus('Comparison failed', 'danger');
        }
    } catch (error) {
        routeInfoDiv.innerHTML = `
            <div class="alert alert-danger animate__animated animate__shakeX">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error: ${error.message}
            </div>
        `;
        showToast('Network error', 'error');
        updateStatus('Connection error', 'danger');
    } finally {
        showLoadingOverlay(false);
    }
}

// Map controls
function setupMapControls() {
    document.getElementById('zoomInBtn').addEventListener('click', () => {
        map.zoomIn();
    });
    
    document.getElementById('zoomOutBtn').addEventListener('click', () => {
        map.zoomOut();
    });
    
    document.getElementById('centerMapBtn').addEventListener('click', () => {
        if (startMarker && endMarker) {
            const group = L.featureGroup([startMarker, endMarker]);
            map.flyToBounds(group.getBounds().pad(0.1));
        } else if (startMarker) {
            map.flyTo(startMarker.getLatLng(), 14);
        } else {
            showToast('No markers to center on', 'error');
        }
    });
}

// Print directions
function printDirections() {
    if (!currentRouteData) {
        showToast('No route to print', 'error');
        return;
    }
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>Route Directions - GPS Navigator</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #007bff; }
                .step { padding: 10px; margin: 10px 0; border-left: 3px solid #28a745; }
                .summary { background: #f8f9fa; padding: 15px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>GPS Navigator - Route Directions</h1>
            <div class="summary">
                <p><strong>Route Type:</strong> ${currentRouteData.type}</p>
                <p><strong>Distance:</strong> ${currentRouteData.distance_km.toFixed(2)} km</p>
                <p><strong>Estimated Time:</strong> ${currentRouteData.travel_time_minutes.toFixed(0)} minutes</p>
            </div>
            <h2>Turn-by-Turn Directions</h2>
            ${currentRouteData.turn_by_turn.map(step => `
                <div class="step">
                    <strong>Step ${step.step}:</strong> ${step.instruction}
                </div>
            `).join('')}
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('GPS Navigator - Interactive UI Loaded ✨');
    
    initMap();
    setupMapControls();
    
    // Main action buttons
    document.getElementById('loadMapBtn').addEventListener('click', loadMap);
    document.getElementById('findRouteBtn').addEventListener('click', findRoute);
    document.getElementById('clearRouteBtn').addEventListener('click', clearRoute);
    document.getElementById('compareRoutesBtn').addEventListener('click', compareRoutes);
    
    // Geocoding buttons
    document.getElementById('geocodeStartBtn').addEventListener('click', function() {
        const address = document.getElementById('startAddress').value;
        if (address) geocodeAddress(address, true);
    });
    
    document.getElementById('geocodeEndBtn').addEventListener('click', function() {
        const address = document.getElementById('endAddress').value;
        if (address) geocodeAddress(address, false);
    });
    
    // Print button
    document.getElementById('printDirectionsBtn').addEventListener('click', printDirections);
    
    // Enter key to geocode
    document.getElementById('startAddress').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            geocodeAddress(this.value, true);
        }
    });
    
    document.getElementById('endAddress').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            geocodeAddress(this.value, false);
        }
    });
    
    // Traffic condition change
    document.getElementById('trafficCondition').addEventListener('change', function() {
        const condition = this.value;
        showToast(`Traffic set to: ${condition}`, 'success');
    });
    
    // Route type change
    document.getElementById('routeType').addEventListener('change', function() {
        const routeType = this.value;
        if (routeType === 'all') {
            showToast('Will compare all route options', 'success');
        }
    });
    
    // Welcome message
    setTimeout(() => {
        showToast('Welcome to GPS Navigator! Load a map to start.', 'success');
    }, 1000);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to find route
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (startCoords && endCoords) {
                findRoute();
            }
        }
        
        // Escape to clear route
        if (e.key === 'Escape') {
            if (startCoords || endCoords) {
                clearRoute();
            }
        }
    });
});
