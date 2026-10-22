"""
A* Pathfinding Algorithm Implementation
Supports multiple heuristics and weighted graphs
"""

import heapq
import math
from typing import Dict, List, Tuple, Optional, Callable


class AStarPathfinder:
    """
    A* algorithm implementation for finding optimal paths in weighted graphs
    """
    
    def __init__(self, graph: Dict, heuristic: str = 'euclidean'):
        """
        Initialize A* pathfinder
        
        Args:
            graph: NetworkX graph with nodes and edges
            heuristic: Type of heuristic ('euclidean', 'manhattan', 'haversine')
        """
        self.graph = graph
        self.heuristic_type = heuristic
        self.nodes_explored = 0
        self.path_cost = 0
        
    def heuristic(self, node1: int, node2: int) -> float:
        """
        Calculate heuristic distance between two nodes
        
        Args:
            node1: Starting node ID
            node2: Target node ID
            
        Returns:
            Estimated distance between nodes
        """
        # Get coordinates
        x1, y1 = self.graph.nodes[node1]['y'], self.graph.nodes[node1]['x']
        x2, y2 = self.graph.nodes[node2]['y'], self.graph.nodes[node2]['x']
        
        if self.heuristic_type == 'euclidean':
            # Euclidean distance
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        elif self.heuristic_type == 'manhattan':
            # Manhattan distance
            return abs(x2 - x1) + abs(y2 - y1)
        
        elif self.heuristic_type == 'haversine':
            # Haversine formula for geographic coordinates (more accurate for lat/lon)
            lat1, lon1 = math.radians(x1), math.radians(y1)
            lat2, lon2 = math.radians(x2), math.radians(y2)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # Radius of earth in kilometers
            r = 6371
            return r * c
        
        else:
            raise ValueError(f"Unknown heuristic type: {self.heuristic_type}")
    
    def find_path(self, start: int, goal: int, 
                  weight: str = 'length',
                  avoid_highways: bool = False) -> Optional[Dict]:
        """
        Find optimal path from start to goal using A* algorithm
        
        Args:
            start: Starting node ID
            goal: Goal node ID
            weight: Edge attribute to use as weight ('length', 'travel_time', etc.)
            avoid_highways: Whether to avoid highways
            
        Returns:
            Dictionary with path, cost, and statistics, or None if no path exists
        """
        # Reset counters
        self.nodes_explored = 0
        self.path_cost = 0
        
        # Check if start and goal nodes exist
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            return None
        
        # Priority queue: (f_score, node, path, g_score)
        frontier = [(0, start, [start], 0)]
        
        # Keep track of best g_score for each node
        best_g_score = {start: 0}
        
        # Explored nodes for visualization
        explored_nodes = []
        
        while frontier:
            # Get node with lowest f_score
            f_score, current, path, g_score = heapq.heappop(frontier)
            
            self.nodes_explored += 1
            explored_nodes.append(current)
            
            # Goal reached
            if current == goal:
                self.path_cost = g_score
                return {
                    'path': path,
                    'cost': g_score,
                    'nodes_explored': self.nodes_explored,
                    'explored_nodes': explored_nodes,
                    'success': True
                }
            
            # Skip if we've found a better path to this node
            if g_score > best_g_score.get(current, float('inf')):
                continue
            
            # Explore neighbors
            for neighbor in self.graph.neighbors(current):
                # Get edge data
                edge_data = self.graph[current][neighbor][0]  # MultiDiGraph
                
                # Skip highways if requested
                if avoid_highways and edge_data.get('highway') in ['motorway', 'trunk']:
                    continue
                
                # Calculate edge cost
                edge_cost = edge_data.get(weight, 1)
                
                # Calculate new g_score
                new_g_score = g_score + edge_cost
                
                # Only consider this path if it's better
                if new_g_score < best_g_score.get(neighbor, float('inf')):
                    best_g_score[neighbor] = new_g_score
                    
                    # Calculate f_score = g_score + heuristic
                    h_score = self.heuristic(neighbor, goal)
                    new_f_score = new_g_score + h_score
                    
                    # Add to frontier
                    new_path = path + [neighbor]
                    heapq.heappush(frontier, (new_f_score, neighbor, new_path, new_g_score))
        
        # No path found
        return {
            'path': [],
            'cost': float('inf'),
            'nodes_explored': self.nodes_explored,
            'explored_nodes': explored_nodes,
            'success': False
        }
    
    def get_path_details(self, path: List[int]) -> Dict:
        """
        Get detailed information about a path
        
        Args:
            path: List of node IDs representing the path
            
        Returns:
            Dictionary with path details including coordinates and turn-by-turn directions
        """
        if not path:
            return {}
        
        details = {
            'coordinates': [],
            'distances': [],
            'total_distance': 0,
            'turn_by_turn': []
        }
        
        for i, node in enumerate(path):
            # Add coordinates
            lat = self.graph.nodes[node]['y']
            lon = self.graph.nodes[node]['x']
            details['coordinates'].append((lat, lon))
            
            # Calculate segment distance
            if i > 0:
                prev_node = path[i-1]
                edge_data = self.graph[prev_node][node][0]
                distance = edge_data.get('length', 0)
                details['distances'].append(distance)
                details['total_distance'] += distance
                
                # Generate turn-by-turn instruction
                street_name = edge_data.get('name', 'Unknown Road')
                details['turn_by_turn'].append({
                    'step': i,
                    'instruction': f"Continue on {street_name} for {distance:.0f} meters",
                    'distance': distance,
                    'coordinates': (lat, lon)
                })
        
        return details


def compare_heuristics(graph, start: int, goal: int) -> Dict:
    """
    Compare different heuristics on the same path
    
    Args:
        graph: NetworkX graph
        start: Starting node
        goal: Goal node
        
    Returns:
        Comparison results for different heuristics
    """
    heuristics = ['euclidean', 'manhattan', 'haversine']
    results = {}
    
    for h in heuristics:
        pathfinder = AStarPathfinder(graph, heuristic=h)
        result = pathfinder.find_path(start, goal)
        
        results[h] = {
            'path_length': len(result['path']) if result['success'] else 0,
            'cost': result['cost'],
            'nodes_explored': result['nodes_explored'],
            'success': result['success']
        }
    
    return results
