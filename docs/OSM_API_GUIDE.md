# 🗺️ OpenStreetMap API Guide - Direct Download

## 📖 What This Does

Downloads **real map data** from OpenStreetMap API **without needing OSMnx**!

---

## 🚀 Quick Start

### Step 1: Install Minimal Requirements
```bash
pip install requests networkx
```
(You probably already have these!)

### Step 2: Run the Downloader
```bash
python osm_direct_download.py
```

This will download a small area of Cairo and show you the data!

---

## 📊 Understanding the API

### OpenStreetMap API URL Format:
```
https://api.openstreetmap.org/api/0.6/map?bbox=LEFT,BOTTOM,RIGHT,TOP
```

### Bounding Box Coordinates:
```
bbox = min_longitude, min_latitude, max_longitude, max_latitude
      └─ WEST ─────┘  └─ SOUTH ───┘  └─ EAST ────┘  └─ NORTH ──┘
```

### Example for Cairo Tahrir Square:
```
https://api.openstreetmap.org/api/0.6/map?bbox=31.230,30.040,31.245,30.055

Breaking it down:
- min_lon (left/west):   31.230
- min_lat (bottom/south): 30.040
- max_lon (right/east):   31.245
- max_lat (top/north):    30.055

This covers about 1.5 km × 1.5 km area
```

---

## 🌍 Coordinate System Explained

### Latitude (North-South):
```
North Pole    +90°
    ↑
Egypt Cairo   +30.04°
Equator        0°
    ↓
South Pole    -90°
```

### Longitude (East-West):
```
←  West                East  →
International Date Line  -180°
Greenwich, London          0°
Cairo, Egypt           +31.23°
International Date Line  +180°
```

### Egypt Coordinates:
```
Cairo:
  Latitude:  30.04°  (30° North of Equator)
  Longitude: 31.23°  (31° East of Greenwich)

Alexandria:
  Latitude:  31.20°
  Longitude: 29.92°

Giza Pyramids:
  Latitude:  29.98°
  Longitude: 31.13°
```

---

## 📏 Bounding Box Size Limits

### API Limits:
```
✅ Maximum: 0.5° × 0.5° (about 55km × 55km)
⚠️ Recommended: 0.02° × 0.02° (about 2km × 2km)
✅ Good for testing: 0.01° × 0.01° (about 1km × 1km)
```

### Why Small Boxes?
- ✅ Faster download
- ✅ Less data to process
- ✅ More reliable
- ✅ Respects OSM server

### Size Comparison:
```
0.001° = ~111 meters  (small street)
0.01°  = ~1.1 km      (neighborhood)
0.1°   = ~11 km       (city district)
0.5°   = ~55 km       (entire city)
```

---

## 💻 Using the Downloader

### Method 1: Use Predefined Cities
```python
from osm_direct_download import OSMDirectDownloader

downloader = OSMDirectDownloader()

# Download predefined area
xml_data = downloader.download_city_area('cairo_tahrir')

# Parse to graph
graph = downloader.parse_xml_to_graph(xml_data)

print(f"Nodes: {len(graph.nodes)}")
print(f"Edges: {len(graph.edges)}")
```

**Available Cities:**
- `cairo_center`
- `cairo_tahrir`
- `cairo_zamalek`
- `giza_pyramids`
- `alexandria_center`
- `sample_small` (for testing)

### Method 2: Custom Bounding Box
```python
downloader = OSMDirectDownloader()

# Your custom area
min_lon, min_lat = 31.230, 30.040  # Bottom-left corner
max_lon, max_lat = 31.240, 30.050  # Top-right corner

xml_data = downloader.download_bbox(
    min_lon, min_lat, max_lon, max_lat,
    output_file='my_area.osm'  # Optional: save XML
)

graph = downloader.parse_xml_to_graph(xml_data)
```

### Method 3: Using wget Command
```bash
# Download directly to file
wget -O cairo.osm "https://api.openstreetmap.org/api/0.6/map?bbox=31.230,30.040,31.245,30.055"

# Then in Python:
with open('cairo.osm', 'r') as f:
    xml_data = f.read()

downloader = OSMDirectDownloader()
graph = downloader.parse_xml_to_graph(xml_data)
```

---

## 📦 What You Get

### XML Data Contains:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6">
  
  <!-- Nodes (intersections, places) -->
  <node id="123456" lat="30.0444" lon="31.2357">
    <tag k="name" v="Tahrir Square"/>
  </node>
  
  <!-- Ways (streets, roads) -->
  <way id="789012">
    <nd ref="123456"/>  <!-- Start node -->
    <nd ref="123457"/>  <!-- End node -->
    <tag k="highway" v="primary"/>
    <tag k="name" v="Qasr Al Nile Street"/>
    <tag k="lanes" v="4"/>
    <tag k="maxspeed" v="60"/>
  </way>
  
</osm>
```

### Converted to Graph:
```python
{
    'nodes': {
        123456: {
            'x': 31.2357,  # longitude
            'y': 30.0444   # latitude
        }
    },
    'edges': {
        (123456, 123457): {
            'length': 523.4,        # meters
            'highway': 'primary',
            'name': 'Qasr Al Nile Street',
            'speed_kph': 60,
            'travel_time': 31.4     # seconds
        }
    }
}
```

---

## 🔧 Integration with Your App

### Replace Demo Data:

**Current demo_app.py:**
```python
# Creates fake data
graph = create_sample_city_graph()
```

**With Real OSM Data:**
```python
from osm_direct_download import OSMDirectDownloader
import pickle
import os

def load_real_map(city_name):
    cache_file = f'cache/{city_name}.pkl'
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    # Download and cache
    downloader = OSMDirectDownloader()
    xml_data = downloader.download_city_area(city_name)
    graph = downloader.parse_xml_to_graph(xml_data)
    
    # Save to cache
    os.makedirs('cache', exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(graph, f)
    
    return graph

# In your Flask app:
@app.route('/api/load_map', methods=['POST'])
def load_map():
    city = request.json.get('place_name', 'cairo_tahrir')
    graph = load_real_map(city)
    # ... rest of your code
```

---

## 🎯 Finding Coordinates

### Method 1: OpenStreetMap Website
1. Go to https://www.openstreetmap.org
2. Search for your location
3. Right-click on map → "Show address"
4. URL shows coordinates: `#map=15/30.0444/31.2357`

### Method 2: Google Maps
1. Go to Google Maps
2. Right-click on location
3. Click the coordinates that appear
4. Copy them

### Method 3: Use Python
```python
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="my_app")
location = geolocator.geocode("Cairo, Egypt")

print(f"Lat: {location.latitude}")
print(f"Lon: {location.longitude}")
```

---

## ⚡ Performance Tips

### 1. Cache Everything
```python
# Save downloaded XML
xml_data = downloader.download_bbox(..., output_file='cairo.osm')

# Save processed graph
import pickle
with open('cairo_graph.pkl', 'wb') as f:
    pickle.dump(graph, f)

# Load from cache (much faster!)
with open('cairo_graph.pkl', 'rb') as f:
    graph = pickle.load(f)
```

### 2. Start Small
```python
# Bad: Too large
bbox = (31.0, 30.0, 31.5, 30.5)  # 55km × 55km ✗

# Good: Small area
bbox = (31.230, 30.040, 31.240, 30.050)  # 1km × 1km ✓
```

### 3. Retry Logic
```python
import time

def download_with_retry(downloader, bbox, max_retries=3):
    for attempt in range(max_retries):
        try:
            return downloader.download_bbox(*bbox)
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait 5 seconds
                continue
            raise
```

---

## 🐛 Troubleshooting

### Problem: Request Timeout
```
✗ Request timed out. Try smaller bounding box.
```
**Solution:** Reduce bounding box size by half

### Problem: Too Much Data
```
✗ Error 400: The maximum bbox size is 0.5
```
**Solution:** Your box is > 0.5° × 0.5°. Make it smaller.

### Problem: No Data Returned
```
✓ Downloaded 500 bytes
✓ Found 0 nodes
```
**Solution:** Your area has no mapped roads. Try different coordinates.

### Problem: Connection Error
```
✗ Error downloading: Connection refused
```
**Solution:** 
- Check internet connection
- OSM API might be down
- Try again in a few minutes

---

## 📊 Data Statistics

### Typical Downloads:

```
Area Size       Nodes    Edges    Download    Processing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0.01° × 0.01°   500     1,000     5 sec       2 sec
(~1km × 1km)

0.02° × 0.02°   2,000   4,000     10 sec      5 sec
(~2km × 2km)

0.05° × 0.05°   12,000  25,000    30 sec      15 sec
(~5km × 5km)

0.1° × 0.1°     50,000  100,000   60 sec      45 sec
(~11km × 11km)
```

---

## 🎓 Complete Example

```python
# complete_example.py
from osm_direct_download import OSMDirectDownloader
import pickle
import os

def download_and_save_cairo():
    """Download Cairo Tahrir area and save for reuse"""
    
    downloader = OSMDirectDownloader()
    
    # Download
    print("Downloading Cairo Tahrir Square...")
    xml_data = downloader.download_city_area(
        'cairo_tahrir',
        output_file='cairo_tahrir.osm'
    )
    
    # Parse
    print("\nParsing XML to graph...")
    graph = downloader.parse_xml_to_graph(xml_data)
    
    # Save processed graph
    print("\nSaving processed graph...")
    with open('cairo_tahrir_graph.pkl', 'wb') as f:
        pickle.dump(graph, f)
    
    print("\n✓ Done! Files created:")
    print("  - cairo_tahrir.osm (raw XML)")
    print("  - cairo_tahrir_graph.pkl (processed graph)")
    
    return graph

def load_cached_graph():
    """Load from cache if available"""
    
    if os.path.exists('cairo_tahrir_graph.pkl'):
        print("Loading from cache...")
        with open('cairo_tahrir_graph.pkl', 'rb') as f:
            return pickle.load(f)
    else:
        print("Cache not found. Downloading...")
        return download_and_save_cairo()

if __name__ == "__main__":
    # First run: Downloads and caches
    # Subsequent runs: Loads from cache (instant!)
    graph = load_cached_graph()
    
    print(f"\nGraph ready!")
    print(f"Nodes: {len(graph.nodes)}")
    print(f"Edges: {len(graph.edges)}")
    
    # Now you can use this with A* algorithm!
```

---

## 🎯 Integration Checklist

To use real OSM data in your app:

- [ ] Install requests: `pip install requests`
- [ ] Test downloader: `python osm_direct_download.py`
- [ ] Choose your area (coordinates)
- [ ] Download and save to cache
- [ ] Update Flask app to use real graph
- [ ] Test pathfinding with real data

---

## 💡 Key Takeaways

1. **API is free** but respect rate limits
2. **Start small** - test with tiny areas first
3. **Cache everything** - don't re-download
4. **Coordinates matter** - double-check them
5. **Real data works** with same A* algorithm!

---

**You can now download REAL map data! 🎉**
