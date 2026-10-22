"""
Test script for GPS Navigator system
Tests core functionality without web interface
"""

import sys
import time
from map_data import MapDataHandler
from astar import AStarPathfinder, compare_heuristics
from traffic_simulator import TrafficSimulator, compare_routes_with_traffic
from route_optimizer import RouteOptimizer


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def test_map_loading():
    """Test 1: Load map data"""
    print_header("TEST 1: Loading Map Data")
    
    try:
        print("Loading map for Piedmont, California...")
        map_handler = MapDataHandler()
        
        # Use a small area for faster testing
        graph = map_handler.load_map_by_place("Piedmont, California, USA", network_type='drive')
        
        stats = map_handler.get_graph_stats()
        print(f"\n✅ Map loaded successfully!")
        print(f"   Nodes: {stats['num_nodes']:,}")
        print(f"   Edges: {stats['num_edges']:,}")
        print(f"   Total length: {stats['total_length_km']:.2f} km")
        
        return map_handler, graph
        
    except Exception as e:
        print(f"\n❌ Error loading map: {e}")
        return None, None


def test_geocoding(map_handler):
    """Test 2: Geocoding"""
    print_header("TEST 2: Geocoding and Reverse Geocoding")
    
    try:
        # Test geocoding
        address = "Berkeley, California"
        print(f"Geocoding address: {address}")
        coords = map_handler.geocode_address(address)
        
        if coords:
            print(f"✅ Coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
            
            # Test reverse geocoding
            print(f"\nReverse geocoding coordinates...")
            reverse_address = map_handler.reverse_geocode(coords[0], coords[1])
            if reverse_address:
                print(f"✅ Address: {reverse_address[:80]}...")
            
            return coords
        else:
            print("❌ Geocoding failed")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_pathfinding(graph, map_handler):
    """Test 3: A* Pathfinding"""
    print_header("TEST 3: A* Pathfinding Algorithm")
    
    try:
        # Get two random nodes that are reasonably far apart
        nodes = list(graph.nodes())
        start_node = nodes[0]
        end_node = nodes[len(nodes) // 2]  # Middle of the graph
        
        print(f"Finding path from node {start_node} to node {end_node}...")
        
        # Test with different heuristics
        print("\nTesting different heuristics:")
        pathfinder = AStarPathfinder(graph, heuristic='haversine')
        
        start_time = time.time()
        result = pathfinder.find_path(start_node, end_node, weight='length')
        end_time = time.time()
        
        if result['success']:
            details = pathfinder.get_path_details(result['path'])
            
            print(f"\n✅ Path found!")
            print(f"   Distance: {details['total_distance']/1000:.2f} km")
            print(f"   Nodes in path: {len(result['path'])}")
            print(f"   Nodes explored: {result['nodes_explored']}")
            print(f"   Search time: {(end_time - start_time)*1000:.2f} ms")
            print(f"   Turn-by-turn steps: {len(details['turn_by_turn'])}")
            
            # Show first 3 directions
            if details['turn_by_turn']:
                print("\nFirst 3 directions:")
                for i, step in enumerate(details['turn_by_turn'][:3]):
                    print(f"   {i+1}. {step['instruction']}")
            
            return start_node, end_node, result
        else:
            print("❌ No path found")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def test_heuristics_comparison(graph, start, end):
    """Test 4: Compare heuristics"""
    print_header("TEST 4: Comparing Different Heuristics")
    
    try:
        print("Comparing Euclidean, Manhattan, and Haversine heuristics...")
        
        results = compare_heuristics(graph, start, end)
        
        print("\nResults:")
        for heuristic, data in results.items():
            if data['success']:
                print(f"\n{heuristic.capitalize()}:")
                print(f"   Path length: {data['path_length']} nodes")
                print(f"   Cost: {data['cost']/1000:.2f} km")
                print(f"   Nodes explored: {data['nodes_explored']}")
        
        print("\n✅ Heuristic comparison complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_traffic_simulation(graph, start, end):
    """Test 5: Traffic simulation"""
    print_header("TEST 5: Traffic Simulation")
    
    try:
        print("Simulating different traffic conditions...")
        
        traffic_sim = TrafficSimulator(graph)
        
        conditions = ['light', 'normal', 'rush_hour', 'heavy']
        
        for condition in conditions:
            traffic_sim.apply_traffic_conditions(condition)
            
            pathfinder = AStarPathfinder(graph, heuristic='haversine')
            result = pathfinder.find_path(start, end, weight='travel_time')
            
            if result['success']:
                travel_time = result['cost'] / 60  # Convert to minutes
                print(f"\n{condition.replace('_', ' ').title()}:")
                print(f"   Travel time: {travel_time:.1f} minutes")
            
            traffic_sim.reset_traffic()
        
        print("\n✅ Traffic simulation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_route_optimization(graph, start, end):
    """Test 6: Route optimization"""
    print_header("TEST 6: Multiple Route Options")
    
    try:
        print("Finding different route options...")
        
        optimizer = RouteOptimizer(graph)
        routes = optimizer.get_all_routes(start, end)
        
        print(f"\nFound {len(routes)} route options:")
        
        for route in routes:
            print(f"\n{route['type'].replace('_', ' ').title()}:")
            print(f"   Distance: {route['distance_km']:.2f} km")
            print(f"   Time: {route['travel_time_minutes']:.1f} minutes")
            print(f"   Nodes explored: {route['nodes_explored']}")
        
        # Compare routes
        comparison = optimizer.compare_routes(routes)
        print(f"\nBest Options:")
        print(f"   Fastest: {comparison['fastest_option']}")
        print(f"   Shortest: {comparison['shortest_option']}")
        
        print("\n✅ Route optimization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def run_all_tests():
    """Run all tests"""
    print_header("GPS NAVIGATOR SYSTEM TEST SUITE")
    print("Testing all components...")
    
    # Test 1: Load map
    map_handler, graph = test_map_loading()
    if not graph:
        print("\n❌ Map loading failed. Cannot continue tests.")
        return
    
    # Test 2: Geocoding
    test_geocoding(map_handler)
    
    # Test 3: Pathfinding
    start, end, result = test_pathfinding(graph, map_handler)
    if not start or not end:
        print("\n❌ Pathfinding failed. Cannot continue tests.")
        return
    
    # Test 4: Heuristics comparison
    test_heuristics_comparison(graph, start, end)
    
    # Test 5: Traffic simulation
    test_traffic_simulation(graph, start, end)
    
    # Test 6: Route optimization
    test_route_optimization(graph, start, end)
    
    # Final summary
    print_header("TEST SUITE COMPLETE")
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Run 'python app.py' to start the web interface")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Try different cities and routes")
    print("4. Share your project on LinkedIn and mention @Syntecxhub")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
