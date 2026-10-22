"""
Map Data Handler - Downloads and manages OpenStreetMap data
"""

import osmnx as ox
import networkx as nx
import pickle
from typing import Tuple, Optional
import os


class MapDataHandler:
    """
    Handles downloading, caching, and managing map data from OpenStreetMap
    """
    
    def __init__(self, cache_dir: str = "map_cache"):
        """
        Initialize map data handler
        
        Args:
            cache_dir: Directory to cache downloaded map data
        """
        self.cache_dir = cache_dir
        self.graph = None
        self.place_name = None
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Configure osmnx
        ox.settings.use_cache = True
        ox.settings.log_console = True
    
    def load_map_by_place(self, place_name: str, 
                          network_type: str = 'drive',
                          force_download: bool = False) -> nx.MultiDiGraph:
        """
        Load map data for a specific place
        
        Args:
            place_name: Name of the place (e.g., "Cairo, Egypt", "Manhattan, New York")
            network_type: Type of street network ('drive', 'walk', 'bike', 'all')
            force_download: Force re-download even if cached
            
        Returns:
            NetworkX MultiDiGraph representing the street network
        """
        cache_file = os.path.join(self.cache_dir, f"{place_name.replace(' ', '_')}_{network_type}.pkl")
        
        # Try to load from cache
        if not force_download and os.path.exists(cache_file):
            print(f"Loading map from cache: {cache_file}")
            with open(cache_file, 'rb') as f:
                self.graph = pickle.load(f)
                self.place_name = place_name
                return self.graph
        
        # Download from OpenStreetMap
        print(f"Downloading map data for {place_name}...")
        try:
            self.graph = ox.graph_from_place(place_name, network_type=network_type)
            self.place_name = place_name
            
            # Add edge speeds and travel times
            self.graph = ox.add_edge_speeds(self.graph)
            self.graph = ox.add_edge_travel_times(self.graph)
            
            # Cache the graph
            with open(cache_file, 'wb') as f:
                pickle.dump(self.graph, f)
            
            print(f"Map downloaded successfully! Nodes: {len(self.graph.nodes)}, Edges: {len(self.graph.edges)}")
            return self.graph
            
        except Exception as e:
            print(f"Error downloading map: {e}")
            raise
    
    def load_map_by_bbox(self, north: float, south: float, 
                         east: float, west: float,
                         network_type: str = 'drive') -> nx.MultiDiGraph:
        """
        Load map data within a bounding box
        
        Args:
            north: Northern latitude
            south: Southern latitude
            east: Eastern longitude
            west: Western longitude
            network_type: Type of street network
            
        Returns:
            NetworkX MultiDiGraph representing the street network
        """
        print(f"Downloading map data for bounding box...")
        try:
            self.graph = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
            
            # Add edge speeds and travel times
            self.graph = ox.add_edge_speeds(self.graph)
            self.graph = ox.add_edge_travel_times(self.graph)
            
            print(f"Map downloaded successfully! Nodes: {len(self.graph.nodes)}, Edges: {len(self.graph.edges)}")
            return self.graph
            
        except Exception as e:
            print(f"Error downloading map: {e}")
            raise
    
    def get_nearest_node(self, lat: float, lon: float) -> int:
        """
        Find the nearest node in the graph to given coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Node ID of nearest node
        """
        if self.graph is None:
            raise ValueError("No map loaded. Call load_map_by_place or load_map_by_bbox first.")
        
        return ox.distance.nearest_nodes(self.graph, lon, lat)
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates
        
        Args:
            address: Street address or place name
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            location = ox.geocode(address)
            return location
        except Exception as e:
            print(f"Error geocoding address: {e}")
            return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to address
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Address string or None if not found
        """
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="gps_navigator")
            location = geolocator.reverse(f"{lat}, {lon}")
            return location.address if location else None
        except Exception as e:
            print(f"Error reverse geocoding: {e}")
            return None
    
    def get_poi(self, poi_type: str, distance: int = 1000) -> list:
        """
        Get points of interest near the map area
        
        Args:
            poi_type: Type of POI (e.g., 'restaurant', 'gas_station', 'hospital')
            distance: Search radius in meters
            
        Returns:
            List of POI locations
        """
        if self.graph is None:
            raise ValueError("No map loaded.")
        
        try:
            # Get map center
            center_lat = sum(self.graph.nodes[node]['y'] for node in self.graph.nodes) / len(self.graph.nodes)
            center_lon = sum(self.graph.nodes[node]['x'] for node in self.graph.nodes) / len(self.graph.nodes)
            
            # Query POIs
            pois = ox.geometries_from_point((center_lat, center_lon), 
                                           tags={poi_type: True}, 
                                           dist=distance)
            
            return pois
        except Exception as e:
            print(f"Error getting POIs: {e}")
            return []
    
    def get_graph_stats(self) -> dict:
        """
        Get statistics about the loaded graph
        
        Returns:
            Dictionary with graph statistics
        """
        if self.graph is None:
            return {}
        
        stats = {
            'num_nodes': len(self.graph.nodes),
            'num_edges': len(self.graph.edges),
            'place_name': self.place_name,
            'average_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes),
        }
        
        # Calculate total network length
        total_length = sum(data.get('length', 0) for _, _, data in self.graph.edges(data=True))
        stats['total_length_km'] = total_length / 1000
        
        return stats


def get_popular_cities() -> dict:
    """
    Return a dictionary of popular cities for quick selection
    
    Returns:
        Dictionary with city names and their bounding boxes
    """
    return {
        'Cairo, Egypt': None,
        'Alexandria, Egypt': None,
        'New York, USA': None,
        'London, UK': None,
        'Paris, France': None,
        'Tokyo, Japan': None,
        'Sydney, Australia': None,
        'Dubai, UAE': None,
    }
