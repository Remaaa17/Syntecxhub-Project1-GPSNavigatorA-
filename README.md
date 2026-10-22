# GPS Navigation System using A* Pathfinding Algorithm

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)
![JavaScript](https://img.shields.io/badge/javascript-ES6+-yellow.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Syntecxhub AI Internship - Week 1 Project**

## Project Overview

This project implements a real-world GPS navigation system using the A* (A-star) pathfinding algorithm. It finds optimal routes between locations in real cities using actual map data from OpenStreetMap, simulates traffic conditions, and provides multiple route options.

## Demo Video

![Demo Video](Demo.mp4)

> Watch the full demonstration of the GPS Navigator in action, showing route planning, traffic simulation, and interactive map features.

**Note:** If the video doesn't play above, you can [download it here](Demo.mp4) or view it directly in the repository files.

## Presentation

📊 **Project Presentation - Available in Multiple Formats:**
- **[PowerPoint (.pptx)](Presentation.pptx)** - Editable presentation file
- **[PDF (.pdf)](Presentation.pdf)** - Universal format, view on any device

The presentation includes:
- Project overview and objectives
- A* algorithm explanation
- System architecture and design
- Features demonstration
- Technical implementation details
- Results and conclusions

## Features

### Core Features (Phase 1)
- **Real Map Data**: Downloads actual street networks from OpenStreetMap
- **A* Pathfinding**: Implements A* algorithm with multiple heuristics
  - Euclidean distance
  - Manhattan distance
  - Haversine distance (for geographic coordinates)
- **Interactive Visualization**: Web-based interface with interactive maps
- **Geocoding**: Convert addresses to coordinates and vice versa

### Advanced Features (Phase 2)
- **Traffic Simulation**: Realistic traffic conditions based on:
  - Time of day (rush hour, midday, night)
  - Day of week (weekday vs weekend)
  - Road type (highway, residential, etc.)
- **Multiple Route Options**:
  - Fastest route (minimal travel time)
  - Shortest route (minimal distance)
  - Highway-free route
  - Scenic route (prefers smaller roads)
  - Fuel-efficient route
- **Turn-by-turn Directions**: Step-by-step navigation instructions
- **ETA Calculation**: Estimated time of arrival

### Extra Features (Phase 3)
- **Web Interface**: Professional Flask-based web application
- **Interactive Map**: Click to set start/end points
- **Route Comparison**: Compare all route options side-by-side
- **Traffic Report**: Real-time traffic statistics
- **Map Caching**: Faster loading with cached map data

## Project Structure

```
Syntecxhub_GPS_Navigator/
├── app.py                 # Flask web application
├── astar.py              # A* algorithm implementation
├── map_data.py           # OpenStreetMap data handler
├── traffic_simulator.py  # Traffic conditions simulation
├── route_optimizer.py    # Multiple route optimization
├── requirements.txt      # Python dependencies
├── map_cache/           # Cached map data
├── static/
│   ├── css/
│   │   └── style.css    # Custom styling
│   └── js/
│       └── map.js       # Frontend JavaScript
├── templates/
│   └── index.html       # Main web interface
└── README.md            # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download

```bash
cd Syntecxhub_GPS_Navigator
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: The first time you run the application, it will download map data which may take a few minutes depending on the city size and your internet connection.

### Step 3: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage Guide

### 1. Load Map Data
1. Select a city from the dropdown (default: Piedmont, CA)
2. Click "Load Map"
3. Wait for map data to download (cached for future use)

### 2. Set Route Points
**Method A**: Click on the map
- First click sets the start point (green marker)
- Second click sets the end point (red marker)

**Method B**: Enter addresses
- Type address in "Start Address" field
- Click "Locate" button
- Repeat for "End Address"

### 3. Find Route
1. Select route type (Fastest, Shortest, etc.)
2. Choose traffic condition
3. Click "Find Route"
4. View route on map and see statistics

### 4. Compare Routes
- Click "Compare All Routes" to see all route options
- Click on any route card to view it on the map
- Compare distance, time, and other metrics

## Testing the Application

### Test Case 1: Basic Pathfinding
```python
# Test with coordinates
Start: 37.8267, -122.2233 (Piedmont, CA)
End: 37.8044, -122.2708 (Berkeley, CA)
Expected: Route found with distance ~5-7 km
```

### Test Case 2: Traffic Simulation
```python
# Same route with different traffic
- Light traffic: ~8-10 minutes
- Normal traffic: ~12-15 minutes
- Rush hour: ~20-25 minutes
- Heavy traffic: ~25-30 minutes
```

### Test Case 3: Route Comparison
```python
# Compare all routes
- Fastest: Uses highways, ~10 min
- Shortest: Direct path, ~5 km
- No Highways: Local roads, ~15 min
- Scenic: Residential areas, ~6 km
```

## Algorithm Details

### A* Algorithm Implementation

The A* algorithm finds the optimal path by using:

**f(n) = g(n) + h(n)**

Where:
- `g(n)` = Actual cost from start to node n
- `h(n)` = Heuristic estimated cost from n to goal
- `f(n)` = Total estimated cost

**Key Features**:
- Priority queue for efficient node selection
- Multiple heuristic options for different use cases
- Support for weighted graphs (traffic, distance, etc.)
- Handles unreachable destinations gracefully

### Heuristic Functions

1. **Euclidean Distance**: Straight-line distance
   ```
   h = √((x₂-x₁)² + (y₂-y₁)²)
   ```

2. **Manhattan Distance**: Grid-based distance
   ```
   h = |x₂-x₁| + |y₂-y₁|
   ```

3. **Haversine Distance**: Geographic distance on Earth's surface
   ```
   Uses latitude/longitude for accurate distances
   ```

## Technical Specifications

### Technologies Used
- **Backend**: Python, Flask
- **Pathfinding**: Custom A* implementation
- **Map Data**: OSMnx, NetworkX
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapping**: Leaflet.js
- **UI Framework**: Bootstrap 5

### Performance
- Typical search time: 100-500ms
- Nodes explored: 500-2000 (depending on distance)
- Map loading: 10-60 seconds (cached afterwards)
- Memory usage: ~200-500 MB (including map data)

## Advanced Features Explained

### Traffic Simulation
The system simulates realistic traffic by:
- Adjusting road speeds based on time of day
- Different factors for highways vs local roads
- Rush hour penalties (40-60% slower)
- Weekend bonuses (10-20% faster)

### Route Optimization
Different optimization criteria:
- **Time**: Minimizes travel time
- **Distance**: Minimizes total distance
- **Fuel**: Balances speed and distance for efficiency
- **Scenic**: Prefers smaller, quieter roads

## Configuration

### Adding New Cities
Edit `map_data.py` and add to `get_popular_cities()`:
```python
'Your City, Country': None,
```

### Adjusting Traffic Parameters
Edit `traffic_simulator.py` and modify:
- `get_traffic_multiplier()` for time-based traffic
- Rush hour time ranges
- Traffic severity factors

## Future Enhancements

Potential improvements:
- [ ] Real-time traffic data integration
- [ ] Multi-stop route planning
- [ ] Voice navigation
- [ ] Mobile app version
- [ ] Public transit integration
- [ ] Bike and walking routes
- [ ] Route sharing functionality
- [ ] Historical traffic patterns

## Contributing

This is an internship project, but suggestions are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is created as part of Syntecxhub AI Internship Program.

## Author

**Eng. Reem Osama**
- Syntecxhub AI Internship - Week 1
- Project: GPS Navigation with A* Algorithm

## Acknowledgments

- OpenStreetMap for map data
- OSMnx library for easy map access
- Syntecxhub for the internship opportunity
- A* algorithm pioneers: Peter Hart, Nils Nilsson, Bertram Raphael

## Contact

For questions or feedback about this project:
- Email: reemosamasaid2004@gmail.com
- Phone: 01070100321

---

Star this repository if you find it helpful!
