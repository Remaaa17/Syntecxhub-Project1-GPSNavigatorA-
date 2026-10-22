"""
GPS Navigator - Easy Launcher Script
Run this file to start the application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the demo app
from src.demo_app import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🗺️  GPS Navigator - Starting Application")
    print("="*60)
    print("\n✨ Features:")
    print("  ✓ A* pathfinding algorithm")
    print("  ✓ Real OpenStreetMap data")
    print("  ✓ Interactive web interface")
    print("  ✓ Multiple route options")
    print("\n🌐 Starting web server...")
    print("  URL: http://localhost:5000")
    print("\n💡 Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
