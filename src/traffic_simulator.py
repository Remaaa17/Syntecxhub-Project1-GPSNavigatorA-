"""
Traffic Simulation Module
Simulates different traffic conditions and updates edge weights accordingly
"""

import random
import networkx as nx
from datetime import datetime, time
from typing import Dict, Literal


class TrafficSimulator:
    """
    Simulates traffic conditions based on time of day, day of week, and road type
    """
    
    def __init__(self, graph: nx.MultiDiGraph):
        """
        Initialize traffic simulator
        
        Args:
            graph: NetworkX graph representing the street network
        """
        self.graph = graph
        self.base_speeds = {}
        
        # Store original speeds
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            self.base_speeds[(u, v, key)] = data.get('speed_kph', 50)
    
    def get_traffic_multiplier(self, 
                               current_time: datetime,
                               road_type: str) -> float:
        """
        Calculate traffic multiplier based on time and road type
        
        Args:
            current_time: Current datetime
            road_type: Type of road (highway, primary, residential, etc.)
            
        Returns:
            Speed multiplier (0.3 = heavy traffic, 1.0 = normal, 1.2 = light traffic)
        """
        hour = current_time.hour
        weekday = current_time.weekday()  # 0 = Monday, 6 = Sunday
        
        # Weekend has lighter traffic
        if weekday >= 5:  # Saturday or Sunday
            base_multiplier = 1.1
        else:
            base_multiplier = 1.0
        
        # Morning rush hour (7-9 AM)
        if 7 <= hour <= 9:
            if road_type in ['motorway', 'trunk', 'primary']:
                return base_multiplier * 0.4  # Heavy traffic on main roads
            else:
                return base_multiplier * 0.7  # Moderate traffic on side roads
        
        # Midday (10 AM - 3 PM)
        elif 10 <= hour <= 15:
            return base_multiplier * 0.9  # Light traffic
        
        # Evening rush hour (4-7 PM)
        elif 16 <= hour <= 19:
            if road_type in ['motorway', 'trunk', 'primary']:
                return base_multiplier * 0.3  # Very heavy traffic on main roads
            else:
                return base_multiplier * 0.6  # Moderate traffic on side roads
        
        # Night time (8 PM - 6 AM)
        elif hour >= 20 or hour <= 6:
            return base_multiplier * 1.2  # Very light traffic
        
        # Default
        return base_multiplier
    
    def apply_traffic_conditions(self, 
                                 condition: Literal['normal', 'rush_hour', 'light', 'heavy'] = 'normal',
                                 current_time: datetime = None) -> nx.MultiDiGraph:
        """
        Apply traffic conditions to the graph
        
        Args:
            condition: Traffic condition preset
            current_time: Specific time to simulate (uses current time if None)
            
        Returns:
            Modified graph with updated travel times
        """
        if current_time is None:
            current_time = datetime.now()
        
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            # Get road type
            road_type = data.get('highway', 'residential')
            if isinstance(road_type, list):
                road_type = road_type[0]
            
            # Get base speed
            base_speed = self.base_speeds.get((u, v, key), 50)
            
            # Calculate multiplier based on condition
            if condition == 'normal':
                multiplier = self.get_traffic_multiplier(current_time, road_type)
            elif condition == 'rush_hour':
                multiplier = 0.4 if road_type in ['motorway', 'trunk', 'primary'] else 0.6
            elif condition == 'light':
                multiplier = 1.2
            elif condition == 'heavy':
                multiplier = 0.3
            else:
                multiplier = 1.0
            
            # Add random variation (±10%)
            multiplier *= random.uniform(0.9, 1.1)
            
            # Update speed and travel time
            new_speed = base_speed * multiplier
            data['speed_kph'] = new_speed
            
            # Recalculate travel time (time = distance / speed)
            length = data.get('length', 100)  # meters
            data['travel_time'] = (length / 1000) / new_speed * 3600  # seconds
        
        return self.graph
    
    def simulate_incident(self, lat: float, lon: float, 
                         radius: int = 500,
                         severity: float = 0.5) -> nx.MultiDiGraph:
        """
        Simulate a traffic incident at a location
        
        Args:
            lat: Latitude of incident
            lon: Longitude of incident
            radius: Affected radius in meters
            severity: Severity of incident (0-1, where 1 is complete blockage)
            
        Returns:
            Modified graph with incident impact
        """
        import osmnx as ox
        
        # Find nearest node
        center_node = ox.distance.nearest_nodes(self.graph, lon, lat)
        
        # Find all nodes within radius
        affected_nodes = []
        for node in self.graph.nodes():
            node_lat = self.graph.nodes[node]['y']
            node_lon = self.graph.nodes[node]['x']
            
            # Calculate distance
            import math
            dist = ox.distance.great_circle(lat, lon, node_lat, node_lon)
            
            if dist <= radius:
                affected_nodes.append(node)
        
        # Reduce speed on edges connected to affected nodes
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            if u in affected_nodes or v in affected_nodes:
                # Reduce speed based on severity
                current_speed = data.get('speed_kph', 50)
                data['speed_kph'] = current_speed * (1 - severity)
                
                # Update travel time
                length = data.get('length', 100)
                data['travel_time'] = (length / 1000) / data['speed_kph'] * 3600
        
        return self.graph
    
    def get_traffic_report(self) -> Dict:
        """
        Generate a traffic report with statistics
        
        Returns:
            Dictionary with traffic statistics
        """
        speeds = []
        travel_times = []
        
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            speeds.append(data.get('speed_kph', 0))
            travel_times.append(data.get('travel_time', 0))
        
        import numpy as np
        
        return {
            'average_speed': np.mean(speeds),
            'min_speed': np.min(speeds),
            'max_speed': np.max(speeds),
            'average_travel_time': np.mean(travel_times),
            'total_edges': len(self.graph.edges)
        }
    
    def reset_traffic(self) -> nx.MultiDiGraph:
        """
        Reset traffic to normal conditions (base speeds)
        
        Returns:
            Graph with reset traffic conditions
        """
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            # Restore base speed
            base_speed = self.base_speeds.get((u, v, key), 50)
            data['speed_kph'] = base_speed
            
            # Recalculate travel time
            length = data.get('length', 100)
            data['travel_time'] = (length / 1000) / base_speed * 3600
        
        return self.graph


def compare_routes_with_traffic(graph, start, goal, pathfinder_class) -> Dict:
    """
    Compare the same route under different traffic conditions
    
    Args:
        graph: NetworkX graph
        start: Start node
        goal: Goal node
        pathfinder_class: AStarPathfinder class
        
    Returns:
        Comparison of routes under different traffic conditions
    """
    conditions = ['light', 'normal', 'rush_hour', 'heavy']
    results = {}
    
    traffic_sim = TrafficSimulator(graph)
    
    for condition in conditions:
        # Apply traffic condition
        traffic_sim.apply_traffic_conditions(condition)
        
        # Find path
        pathfinder = pathfinder_class(graph)
        result = pathfinder.find_path(start, goal, weight='travel_time')
        
        results[condition] = {
            'path_length': len(result['path']) if result['success'] else 0,
            'travel_time': result['cost'],
            'success': result['success']
        }
        
        # Reset traffic
        traffic_sim.reset_traffic()
    
    return results
