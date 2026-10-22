"""
Demo GPS Navigator - Works WITHOUT osmnx
Uses pre-generated sample data OR real OSM data to demonstrate A* pathfinding
"""

from flask import Flask, render_template, jsonify, request
import networkx as nx
import random
import json
import math
import pickle
import os
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.osm_direct_download import OSMDirectDownloader

# Set correct paths for templates and static files
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Global variables
current_graph = None
graph_stats = {}
osm_downloader = OSMDirectDownloader()


def create_sample_city_graph(city_name="Sample City", size=50):
    """Create a sample city graph without needing OSMnx"""
    G = nx.grid_2d_graph(size, size)
    
    # Convert to directed graph with attributes
    DG = nx.DiGraph()
    
    # Add nodes with coordinates
    for node in G.nodes():
        x, y = node
        # Simulate lat/lon coordinates (around Cairo as example)
        lat = 30.0444 + (y * 0.001)
        lon = 31.2357 + (x * 0.001)
        DG.add_node(node, x=lon, y=lat)
    
    # Add edges with length and speed
    for u, v in G.edges():
        # Calculate distance
        x1, y1 = DG.nodes[u]['x'], DG.nodes[u]['y']
        x2, y2 = DG.nodes[v]['x'], DG.nodes[v]['y']
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2) * 111000  # Convert to meters
        
        # Random road type
        road_types = ['residential', 'primary', 'secondary', 'tertiary']
        highway = random.choice(road_types)
        
        # Speed based on road type
        speeds = {'residential': 30, 'primary': 60, 'secondary': 50, 'tertiary': 40}
        speed = speeds[highway]
        
        # Travel time
        travel_time = (length / 1000) / speed * 3600  # seconds
        
        # Add edge in both directions
        DG.add_edge(u, v, length=length, highway=highway, speed_kph=speed, travel_time=travel_time)
        DG.add_edge(v, u, length=length, highway=highway, speed_kph=speed, travel_time=travel_time)
    
    # Remove some random edges to create more interesting paths
    edges_to_remove = random.sample(list(DG.edges()), len(DG.edges()) // 20)
    DG.remove_edges_from(edges_to_remove)
    
    return DG


def heuristic_distance(node1, node2, graph):
    """Calculate heuristic distance between two nodes"""
    x1, y1 = graph.nodes[node1]['x'], graph.nodes[node1]['y']
    x2, y2 = graph.nodes[node2]['x'], graph.nodes[node2]['y']
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) * 111000  # Convert to meters


def astar_path(graph, start, goal, weight='length'):
    """A* pathfinding algorithm"""
    import heapq
    
    if start not in graph or goal not in graph:
        return None
    
    frontier = [(0, start, [start], 0)]
    best_g_score = {start: 0}
    nodes_explored = 0
    
    while frontier:
        f_score, current, path, g_score = heapq.heappop(frontier)
        nodes_explored += 1
        
        if current == goal:
            return {
                'path': path,
                'cost': g_score,
                'nodes_explored': nodes_explored
            }
        
        if g_score > best_g_score.get(current, float('inf')):
            continue
        
        for neighbor in graph.neighbors(current):
            edge_data = graph[current][neighbor]
            edge_cost = edge_data.get(weight, 1)
            new_g_score = g_score + edge_cost
            
            if new_g_score < best_g_score.get(neighbor, float('inf')):
                best_g_score[neighbor] = new_g_score
                h_score = heuristic_distance(neighbor, goal, graph)
                new_f_score = new_g_score + h_score
                new_path = path + [neighbor]
                heapq.heappush(frontier, (new_f_score, neighbor, new_path, new_g_score))
    
    return None


@app.route('/')
def index():
    return render_template('demo_index.html')


def load_real_osm_map(city_name):
    """Load real map data from OpenStreetMap"""
    global osm_downloader
    
    # Cache in parent directory
    cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f'{city_name}.pkl')
    
    # Check cache first
    if os.path.exists(cache_file):
        print(f"Loading {city_name} from cache...")
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Download from OSM
    print(f"Downloading {city_name} from OpenStreetMap...")
    try:
        xml_data = osm_downloader.download_city_area(city_name)
        if xml_data is None:
            return None
        
        # Parse to graph
        graph = osm_downloader.parse_xml_to_graph(xml_data)
        
        # Cache for future use
        with open(cache_file, 'wb') as f:
            pickle.dump(graph, f)
        print(f"✓ Cached to {cache_file}")
        
        return graph
    except Exception as e:
        print(f"Error downloading OSM data: {e}")
        return None


@app.route('/api/load_map', methods=['POST'])
def load_map():
    global current_graph, graph_stats
    
    data = request.json
    place_name = data.get('place_name', 'Sample City')
    use_real_data = data.get('use_real_data', False)
    
    # Try to load real OSM data if requested
    if use_real_data:
        print(f"\n🌍 Loading REAL map data for: {place_name}")
        current_graph = load_real_osm_map(place_name)
        
        if current_graph is None:
            print("⚠️ Failed to load real data, falling back to sample data")
            current_graph = create_sample_city_graph(place_name)
            data_source = 'sample (fallback)'
        else:
            print(f"✓ Real OSM data loaded successfully!")
            data_source = 'OpenStreetMap (real)'
    else:
        print(f"\n📊 Loading SAMPLE data for: {place_name}")
        current_graph = create_sample_city_graph(place_name)
        data_source = 'sample (generated)'
    
    # Calculate stats
    total_length = sum(d.get('length', 0) for _, _, d in current_graph.edges(data=True))
    
    graph_stats = {
        'num_nodes': current_graph.number_of_nodes(),
        'num_edges': current_graph.number_of_edges(),
        'total_length_km': total_length / 1000,
        'place_name': place_name,
        'data_source': data_source
    }
    
    # Get bounds
    lats = [current_graph.nodes[n]['y'] for n in current_graph.nodes()]
    lons = [current_graph.nodes[n]['x'] for n in current_graph.nodes()]
    
    bounds = {
        'north': max(lats),
        'south': min(lats),
        'east': max(lons),
        'west': min(lons),
        'center': [(max(lats) + min(lats)) / 2, (max(lons) + min(lons)) / 2]
    }
    
    return jsonify({
        'success': True,
        'stats': graph_stats,
        'bounds': bounds,
        'message': f'Map loaded: {data_source}'
    })


@app.route('/api/find_route', methods=['POST'])
def find_route():
    global current_graph
    
    if current_graph is None:
        return jsonify({'success': False, 'error': 'Map not loaded'}), 400
    
    data = request.json
    start_lat = data.get('start_lat')
    start_lon = data.get('start_lon')
    end_lat = data.get('end_lat')
    end_lon = data.get('end_lon')
    weight = 'travel_time' if data.get('route_type') == 'fastest' else 'length'
    
    # Find nearest nodes
    def find_nearest_node(lat, lon):
        min_dist = float('inf')
        nearest = None
        for node in current_graph.nodes():
            node_lat = current_graph.nodes[node]['y']
            node_lon = current_graph.nodes[node]['x']
            dist = (node_lat - lat)**2 + (node_lon - lon)**2
            if dist < min_dist:
                min_dist = dist
                nearest = node
        return nearest
    
    start_node = find_nearest_node(start_lat, start_lon)
    end_node = find_nearest_node(end_lat, end_lon)
    
    print(f"\n🔍 Route Request:")
    print(f"   Start: ({start_lat:.6f}, {start_lon:.6f}) → Node {start_node}")
    print(f"   End:   ({end_lat:.6f}, {end_lon:.6f}) → Node {end_node}")
    
    # Check if nodes are in the same connected component
    try:
        # For directed graph, check weak connectivity
        if not nx.has_path(current_graph, start_node, end_node):
            print(f"   ✗ No path exists between these nodes (disconnected components)")
            
            # Find alternative suggestions
            # Get largest connected component
            if current_graph.is_directed():
                components = list(nx.weakly_connected_components(current_graph))
            else:
                components = list(nx.connected_components(current_graph))
            
            largest_component = max(components, key=len)
            
            return jsonify({
                'success': False, 
                'error': 'No route found - points are in disconnected areas',
                'suggestion': f'Try clicking points closer together. The map has {len(components)} separate areas. Largest area has {len(largest_component)} nodes.'
            }), 404
    except:
        pass
    
    # Find path
    result = astar_path(current_graph, start_node, end_node, weight)
    
    if result is None:
        print(f"   ✗ A* algorithm couldn't find path")
        return jsonify({
            'success': False, 
            'error': 'No route found - try different points closer together'
        }), 404
    
    print(f"   ✓ Path found! {len(result['path'])} nodes, explored {result['nodes_explored']} nodes")
    
    # Get path details
    coordinates = []
    total_distance = 0
    turn_by_turn = []
    
    for i, node in enumerate(result['path']):
        lat = current_graph.nodes[node]['y']
        lon = current_graph.nodes[node]['x']
        coordinates.append([lat, lon])
        
        if i > 0:
            prev_node = result['path'][i-1]
            edge_data = current_graph[prev_node][node]
            distance = edge_data.get('length', 0)
            total_distance += distance
            
            turn_by_turn.append({
                'step': i,
                'instruction': f"Continue for {distance:.0f} meters",
                'distance': distance,
                'coordinates': [lat, lon]
            })
    
    # Calculate travel time
    total_time = result['cost'] / 60 if weight == 'travel_time' else (total_distance / 1000) / 40 * 60
    
    route_data = {
        'type': data.get('route_type', 'fastest'),
        'path': result['path'],
        'coordinates': coordinates,
        'distance_km': total_distance / 1000,
        'distance_meters': total_distance,
        'travel_time_minutes': total_time,
        'travel_time_seconds': total_time * 60,
        'nodes_explored': result['nodes_explored'],
        'turn_by_turn': turn_by_turn
    }
    
    return jsonify({
        'success': True,
        'route': route_data
    })


@app.route('/api/compare_routes', methods=['POST'])
def compare_routes():
    # For demo, just return the same route with slight variations
    route_response = find_route()
    if route_response.status_code != 200:
        return route_response
    
    base_route = route_response.get_json()['route']
    
    routes = [
        {**base_route, 'type': 'fastest'},
        {**base_route, 'type': 'shortest', 'travel_time_minutes': base_route['travel_time_minutes'] * 1.1},
        {**base_route, 'type': 'scenic', 'travel_time_minutes': base_route['travel_time_minutes'] * 1.2}
    ]
    
    comparison = {
        'fastest_option': 'fastest',
        'shortest_option': 'shortest'
    }
    
    return jsonify({
        'success': True,
        'routes': routes,
        'comparison': comparison
    })


@app.route('/api/available_cities', methods=['GET'])
def available_cities():
    """Return list of available OSM cities"""
    cities = [
        {'id': 'cairo_center', 'name': 'Cairo City Center', 'real': True},
        {'id': 'cairo_tahrir', 'name': 'Cairo - Tahrir Square', 'real': True},
        {'id': 'cairo_zamalek', 'name': 'Cairo - Zamalek', 'real': True},
        {'id': 'giza_pyramids', 'name': 'Giza - Pyramids Area', 'real': True},
        {'id': 'alexandria_center', 'name': 'Alexandria City Center', 'real': True},
        {'id': 'sample_small', 'name': 'Sample Small Area (Testing)', 'real': True},
        {'id': 'Sample City', 'name': 'Generated Sample Data', 'real': False}
    ]
    
    return jsonify({
        'success': True,
        'cities': cities
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🗺️  GPS Navigator - Demo Version")
    print("  A* Pathfinding with Sample Data")
    print("="*60)
    print("\n✨ Features:")
    print("  ✓ A* pathfinding algorithm")
    print("  ✓ Interactive web interface")
    print("  ✓ Multiple route options")
    print("  ✓ Turn-by-turn directions")
    print("\n🌐 Opening web server...")
    print("  URL: http://localhost:5000")
    print("\n💡 This demo uses sample data instead of real maps")
    print("  (OSMnx not installed)")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
