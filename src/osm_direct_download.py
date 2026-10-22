"""
Direct OpenStreetMap API Downloader
Downloads map data without OSMnx dependency
"""

import requests
import xml.etree.ElementTree as ET
import networkx as nx
import json
import time
from datetime import datetime


class OSMDirectDownloader:
    """
    Download and parse OpenStreetMap data directly from API
    """
    
    def __init__(self):
        self.api_base = "https://api.openstreetmap.org/api/0.6"
        self.timeout = 60  # seconds
        
    def download_bbox(self, min_lon, min_lat, max_lon, max_lat, output_file=None):
        """
        Download map data for a bounding box
        
        Args:
            min_lon: Minimum longitude (west, left)
            min_lat: Minimum latitude (south, bottom)
            max_lon: Maximum longitude (east, right)
            max_lat: Maximum latitude (north, top)
            output_file: Optional file to save raw XML
            
        Returns:
            XML string with map data
        """
        # Construct URL
        # Format: bbox=left,bottom,right,top
        bbox = f"{min_lon},{min_lat},{max_lon},{max_lat}"
        url = f"{self.api_base}/map?bbox={bbox}"
        
        print(f"Downloading from: {url}")
        print(f"Bounding box: {bbox}")
        print(f"This may take 10-30 seconds...")
        
        try:
            # Download data
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            xml_data = response.text
            
            # Save to file if requested
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(xml_data)
                print(f"✓ Saved raw data to: {output_file}")
            
            print(f"✓ Downloaded {len(xml_data)} bytes")
            return xml_data
            
        except requests.exceptions.Timeout:
            print("✗ Request timed out. Try smaller bounding box.")
            raise
        except requests.exceptions.RequestException as e:
            print(f"✗ Error downloading: {e}")
            raise
    
    def parse_xml_to_graph(self, xml_data):
        """
        Parse OSM XML and convert to NetworkX graph
        
        Args:
            xml_data: XML string from OSM API
            
        Returns:
            NetworkX DiGraph
        """
        print("\nParsing XML data...")
        
        # Parse XML
        root = ET.fromstring(xml_data)
        
        # Extract nodes (intersections)
        nodes = {}
        for node in root.findall('node'):
            node_id = int(node.get('id'))
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            nodes[node_id] = {'lat': lat, 'lon': lon}
        
        print(f"✓ Found {len(nodes)} nodes (intersections)")
        
        # Extract ways (streets)
        ways = []
        for way in root.findall('way'):
            way_id = int(way.get('id'))
            
            # Get nodes in this way
            node_refs = [int(nd.get('ref')) for nd in way.findall('nd')]
            
            # Get tags (metadata)
            tags = {}
            for tag in way.findall('tag'):
                tags[tag.get('k')] = tag.get('v')
            
            # Only include roads (has highway tag)
            if 'highway' in tags:
                ways.append({
                    'id': way_id,
                    'nodes': node_refs,
                    'tags': tags
                })
        
        print(f"✓ Found {len(ways)} ways (streets)")
        
        # Build NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes to graph
        for node_id, data in nodes.items():
            G.add_node(node_id, 
                      x=data['lon'],  # longitude
                      y=data['lat'])  # latitude
        
        # Add edges from ways
        edges_added = 0
        for way in ways:
            highway_type = way['tags'].get('highway', 'residential')
            name = way['tags'].get('name', 'Unnamed Road')
            oneway = way['tags'].get('oneway', 'no') == 'yes'
            
            # Speed limits by road type (km/h)
            speed_map = {
                'motorway': 100,
                'trunk': 80,
                'primary': 60,
                'secondary': 50,
                'tertiary': 40,
                'residential': 30,
                'service': 20
            }
            speed = speed_map.get(highway_type, 40)
            
            # Connect consecutive nodes
            for i in range(len(way['nodes']) - 1):
                node1 = way['nodes'][i]
                node2 = way['nodes'][i + 1]
                
                # Skip if nodes don't exist
                if node1 not in G.nodes or node2 not in G.nodes:
                    continue
                
                # Calculate distance
                lat1, lon1 = G.nodes[node1]['y'], G.nodes[node1]['x']
                lat2, lon2 = G.nodes[node2]['y'], G.nodes[node2]['x']
                
                # Haversine distance (approximate)
                import math
                R = 6371000  # Earth radius in meters
                
                phi1, phi2 = math.radians(lat1), math.radians(lat2)
                dphi = math.radians(lat2 - lat1)
                dlambda = math.radians(lon2 - lon1)
                
                a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                distance = R * c  # meters
                
                # Travel time
                travel_time = (distance / 1000) / speed * 3600  # seconds
                
                # Add edge(s)
                G.add_edge(node1, node2,
                          length=distance,
                          highway=highway_type,
                          name=name,
                          speed_kph=speed,
                          travel_time=travel_time)
                edges_added += 1
                
                # Add reverse edge if not oneway
                if not oneway:
                    G.add_edge(node2, node1,
                              length=distance,
                              highway=highway_type,
                              name=name,
                              speed_kph=speed,
                              travel_time=travel_time)
                    edges_added += 1
        
        print(f"✓ Added {edges_added} edges (connections)")
        
        # Remove isolated nodes (not connected to any way)
        isolated = list(nx.isolates(G))
        G.remove_nodes_from(isolated)
        print(f"✓ Removed {len(isolated)} isolated nodes")
        
        print(f"\n✓ Final graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
        
        return G
    
    def download_city_area(self, city_name, output_file=None):
        """
        Download map for common city areas (predefined bounding boxes)
        
        Args:
            city_name: Name of city
            output_file: Optional file to save data
        """
        # Predefined bounding boxes for common cities
        # Format: (min_lon, min_lat, max_lon, max_lat)
        cities = {
            'cairo_center': (31.23, 30.04, 31.26, 30.07),
            'cairo_tahrir': (31.230, 30.040, 31.245, 30.055),
            'cairo_zamalek': (31.215, 30.055, 31.230, 30.070),
            'giza_pyramids': (31.125, 29.970, 31.140, 29.985),
            'alexandria_center': (29.90, 31.19, 29.93, 31.22),
            'new_york_manhattan': (-74.01, 40.75, -73.99, 40.77),
            'london_center': (-0.13, 51.50, -0.11, 51.52),
            'paris_center': (2.33, 48.85, 2.36, 48.87),
            'sample_small': (31.230, 30.040, 31.240, 30.050),  # Very small for testing
        }
        
        if city_name.lower() not in cities:
            print(f"City '{city_name}' not found. Available cities:")
            for city in cities.keys():
                print(f"  - {city}")
            return None
        
        bbox = cities[city_name.lower()]
        return self.download_bbox(*bbox, output_file)


def example_usage():
    """
    Example: Download and process map data
    """
    print("="*60)
    print("  OpenStreetMap Direct Downloader")
    print("="*60)
    
    downloader = OSMDirectDownloader()
    
    # Example 1: Download small area in Cairo
    print("\n[Example 1] Downloading Cairo Tahrir Square area...")
    
    try:
        # Download XML data
        xml_data = downloader.download_city_area('cairo_tahrir', 'cairo_tahrir.osm')
        
        # Parse to graph
        graph = downloader.parse_xml_to_graph(xml_data)
        
        # Show statistics
        print("\n" + "="*60)
        print("  Success!")
        print("="*60)
        print(f"Nodes (intersections): {len(graph.nodes)}")
        print(f"Edges (streets): {len(graph.edges)}")
        
        # Show sample node
        sample_node = list(graph.nodes())[0]
        print(f"\nSample node {sample_node}:")
        print(f"  Lat: {graph.nodes[sample_node]['y']:.6f}")
        print(f"  Lon: {graph.nodes[sample_node]['x']:.6f}")
        
        # Show sample edge
        if len(graph.edges) > 0:
            sample_edge = list(graph.edges(data=True))[0]
            print(f"\nSample edge:")
            print(f"  From: {sample_edge[0]}")
            print(f"  To: {sample_edge[1]}")
            print(f"  Length: {sample_edge[2]['length']:.1f} meters")
            print(f"  Type: {sample_edge[2]['highway']}")
            print(f"  Speed: {sample_edge[2]['speed_kph']} km/h")
        
        return graph
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTips:")
        print("  - Check internet connection")
        print("  - Try smaller bounding box")
        print("  - Wait and retry if OSM is busy")
        return None


if __name__ == "__main__":
    # Run example
    graph = example_usage()
    
    if graph:
        print("\n✓ You can now use this graph with A* algorithm!")
        print("\nNext steps:")
        print("  1. Save graph: import pickle; pickle.dump(graph, open('graph.pkl', 'wb'))")
        print("  2. Use with A* algorithm")
        print("  3. Integrate with your Flask app")
