"""
Route Optimizer - Provides multiple route options based on different criteria
"""

import networkx as nx
from typing import Dict, List, Tuple
from astar import AStarPathfinder


class RouteOptimizer:
    """
    Generates multiple route options optimized for different criteria
    """
    
    def __init__(self, graph: nx.MultiDiGraph):
        """
        Initialize route optimizer
        
        Args:
            graph: NetworkX graph representing the street network
        """
        self.graph = graph
    
    def get_fastest_route(self, start: int, goal: int) -> Dict:
        """
        Get the fastest route based on travel time
        
        Args:
            start: Start node ID
            goal: Goal node ID
            
        Returns:
            Route information dictionary
        """
        pathfinder = AStarPathfinder(self.graph, heuristic='haversine')
        result = pathfinder.find_path(start, goal, weight='travel_time')
        
        if result['success']:
            details = pathfinder.get_path_details(result['path'])
            return {
                'type': 'fastest',
                'path': result['path'],
                'travel_time_seconds': result['cost'],
                'travel_time_minutes': result['cost'] / 60,
                'distance_meters': details['total_distance'],
                'distance_km': details['total_distance'] / 1000,
                'coordinates': details['coordinates'],
                'turn_by_turn': details['turn_by_turn'],
                'nodes_explored': result['nodes_explored']
            }
        return {'success': False}
    
    def get_shortest_route(self, start: int, goal: int) -> Dict:
        """
        Get the shortest route based on distance
        
        Args:
            start: Start node ID
            goal: Goal node ID
            
        Returns:
            Route information dictionary
        """
        pathfinder = AStarPathfinder(self.graph, heuristic='haversine')
        result = pathfinder.find_path(start, goal, weight='length')
        
        if result['success']:
            details = pathfinder.get_path_details(result['path'])
            
            # Calculate travel time for shortest path
            total_time = 0
            for i in range(len(result['path']) - 1):
                u, v = result['path'][i], result['path'][i+1]
                edge_data = self.graph[u][v][0]
                total_time += edge_data.get('travel_time', 0)
            
            return {
                'type': 'shortest',
                'path': result['path'],
                'distance_meters': result['cost'],
                'distance_km': result['cost'] / 1000,
                'travel_time_seconds': total_time,
                'travel_time_minutes': total_time / 60,
                'coordinates': details['coordinates'],
                'turn_by_turn': details['turn_by_turn'],
                'nodes_explored': result['nodes_explored']
            }
        return {'success': False}
    
    def get_highway_free_route(self, start: int, goal: int) -> Dict:
        """
        Get route that avoids highways/motorways
        
        Args:
            start: Start node ID
            goal: Goal node ID
            
        Returns:
            Route information dictionary
        """
        pathfinder = AStarPathfinder(self.graph, heuristic='haversine')
        result = pathfinder.find_path(start, goal, weight='travel_time', avoid_highways=True)
        
        if result['success']:
            details = pathfinder.get_path_details(result['path'])
            return {
                'type': 'no_highways',
                'path': result['path'],
                'travel_time_seconds': result['cost'],
                'travel_time_minutes': result['cost'] / 60,
                'distance_meters': details['total_distance'],
                'distance_km': details['total_distance'] / 1000,
                'coordinates': details['coordinates'],
                'turn_by_turn': details['turn_by_turn'],
                'nodes_explored': result['nodes_explored']
            }
        return {'success': False}
    
    def get_scenic_route(self, start: int, goal: int, 
                        max_detour_factor: float = 1.3) -> Dict:
        """
        Get a scenic route (prefers smaller roads, parks nearby)
        
        Args:
            start: Start node ID
            goal: Goal node ID
            max_detour_factor: Maximum allowed detour (1.3 = 30% longer)
            
        Returns:
            Route information dictionary
        """
        # Create modified graph with preferences for smaller roads
        scenic_graph = self.graph.copy()
        
        for u, v, key, data in scenic_graph.edges(keys=True, data=True):
            road_type = data.get('highway', 'residential')
            if isinstance(road_type, list):
                road_type = road_type[0]
            
            # Preference scoring (lower is better for scenic routes)
            if road_type in ['residential', 'unclassified', 'tertiary']:
                preference = 0.8  # Prefer these
            elif road_type in ['secondary', 'primary']:
                preference = 1.0  # Neutral
            else:
                preference = 1.5  # Avoid highways
            
            # Adjust travel time based on preference
            data['scenic_weight'] = data.get('travel_time', 100) * preference
        
        pathfinder = AStarPathfinder(scenic_graph, heuristic='haversine')
        result = pathfinder.find_path(start, goal, weight='scenic_weight')
        
        if result['success']:
            details = pathfinder.get_path_details(result['path'])
            
            # Calculate actual travel time
            total_time = 0
            for i in range(len(result['path']) - 1):
                u, v = result['path'][i], result['path'][i+1]
                edge_data = self.graph[u][v][0]
                total_time += edge_data.get('travel_time', 0)
            
            return {
                'type': 'scenic',
                'path': result['path'],
                'travel_time_seconds': total_time,
                'travel_time_minutes': total_time / 60,
                'distance_meters': details['total_distance'],
                'distance_km': details['total_distance'] / 1000,
                'coordinates': details['coordinates'],
                'turn_by_turn': details['turn_by_turn'],
                'nodes_explored': result['nodes_explored']
            }
        return {'success': False}
    
    def get_fuel_efficient_route(self, start: int, goal: int) -> Dict:
        """
        Get route optimized for fuel efficiency (fewer stops, moderate speed)
        
        Args:
            start: Start node ID
            goal: Goal node ID
            
        Returns:
            Route information dictionary
        """
        # Create modified graph with fuel efficiency weights
        fuel_graph = self.graph.copy()
        
        for u, v, key, data in fuel_graph.edges(keys=True, data=True):
            speed = data.get('speed_kph', 50)
            length = data.get('length', 100)
            
            # Optimal fuel efficiency around 60-80 km/h
            if 60 <= speed <= 80:
                efficiency = 0.9
            elif 40 <= speed <= 100:
                efficiency = 1.0
            else:
                efficiency = 1.2  # Penalty for very slow or very fast
            
            data['fuel_weight'] = (length / 1000) * efficiency
        
        pathfinder = AStarPathfinder(fuel_graph, heuristic='haversine')
        result = pathfinder.find_path(start, goal, weight='fuel_weight')
        
        if result['success']:
            details = pathfinder.get_path_details(result['path'])
            
            # Calculate actual travel time
            total_time = 0
            for i in range(len(result['path']) - 1):
                u, v = result['path'][i], result['path'][i+1]
                edge_data = self.graph[u][v][0]
                total_time += edge_data.get('travel_time', 0)
            
            return {
                'type': 'fuel_efficient',
                'path': result['path'],
                'travel_time_seconds': total_time,
                'travel_time_minutes': total_time / 60,
                'distance_meters': details['total_distance'],
                'distance_km': details['total_distance'] / 1000,
                'coordinates': details['coordinates'],
                'turn_by_turn': details['turn_by_turn'],
                'nodes_explored': result['nodes_explored'],
                'estimated_fuel_saving': '15%'  # Placeholder
            }
        return {'success': False}
    
    def get_all_routes(self, start: int, goal: int) -> List[Dict]:
        """
        Get all available route options
        
        Args:
            start: Start node ID
            goal: Goal node ID
            
        Returns:
            List of route dictionaries
        """
        routes = []
        
        # Get fastest route
        fastest = self.get_fastest_route(start, goal)
        if fastest.get('success', True):
            routes.append(fastest)
        
        # Get shortest route
        shortest = self.get_shortest_route(start, goal)
        if shortest.get('success', True):
            routes.append(shortest)
        
        # Get highway-free route
        no_highway = self.get_highway_free_route(start, goal)
        if no_highway.get('success', True):
            routes.append(no_highway)
        
        # Get fuel-efficient route
        fuel_efficient = self.get_fuel_efficient_route(start, goal)
        if fuel_efficient.get('success', True):
            routes.append(fuel_efficient)
        
        return routes
    
    def compare_routes(self, routes: List[Dict]) -> Dict:
        """
        Compare multiple routes and provide summary
        
        Args:
            routes: List of route dictionaries
            
        Returns:
            Comparison summary
        """
        if not routes:
            return {}
        
        comparison = {
            'num_routes': len(routes),
            'routes_summary': []
        }
        
        for route in routes:
            comparison['routes_summary'].append({
                'type': route['type'],
                'distance_km': route['distance_km'],
                'time_minutes': route['travel_time_minutes'],
                'num_turns': len(route.get('turn_by_turn', []))
            })
        
        # Find best options
        fastest_route = min(routes, key=lambda r: r['travel_time_minutes'])
        shortest_route = min(routes, key=lambda r: r['distance_km'])
        
        comparison['fastest_option'] = fastest_route['type']
        comparison['shortest_option'] = shortest_route['type']
        
        return comparison
