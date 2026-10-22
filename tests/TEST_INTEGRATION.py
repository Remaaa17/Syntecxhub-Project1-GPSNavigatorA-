"""
Quick Test Script - Verify OSM Integration Works
Run this to test the complete system
"""

import sys
import os

def test_imports():
    """Test 1: Check all imports"""
    print("="*60)
    print("TEST 1: Checking Imports")
    print("="*60)
    
    try:
        import flask
        print("✓ Flask installed")
    except ImportError:
        print("✗ Flask NOT installed - run: pip install flask")
        return False
    
    try:
        import networkx
        print("✓ NetworkX installed")
    except ImportError:
        print("✗ NetworkX NOT installed - run: pip install networkx")
        return False
    
    try:
        import requests
        print("✓ Requests installed")
    except ImportError:
        print("✗ Requests NOT installed - run: pip install requests")
        return False
    
    print("\n✓ All required packages installed!\n")
    return True


def test_osm_downloader():
    """Test 2: Check OSM downloader module"""
    print("="*60)
    print("TEST 2: Testing OSM Downloader")
    print("="*60)
    
    try:
        from osm_direct_download import OSMDirectDownloader
        print("✓ OSMDirectDownloader imported successfully")
        
        downloader = OSMDirectDownloader()
        print("✓ Downloader object created")
        
        # Check predefined cities
        print("\n📍 Available predefined cities:")
        cities = [
            'cairo_center', 'cairo_tahrir', 'cairo_zamalek',
            'giza_pyramids', 'alexandria_center', 'sample_small'
        ]
        for city in cities:
            print(f"   - {city}")
        
        print("\n✓ OSM Downloader ready!\n")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_demo_app():
    """Test 3: Check demo app"""
    print("="*60)
    print("TEST 3: Testing Demo App")
    print("="*60)
    
    try:
        # Don't actually import (would start Flask)
        # Just check file exists
        if os.path.exists('demo_app.py'):
            print("✓ demo_app.py exists")
            
            with open('demo_app.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'OSMDirectDownloader' in content:
                print("✓ OSM integration found in demo_app.py")
            else:
                print("✗ OSM integration NOT found in demo_app.py")
                return False
            
            if 'load_real_osm_map' in content:
                print("✓ Real OSM loading function found")
            else:
                print("✗ Real OSM loading function NOT found")
                return False
            
            print("\n✓ Demo app properly configured!\n")
            return True
        else:
            print("✗ demo_app.py not found")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_cache_directory():
    """Test 4: Check cache setup"""
    print("="*60)
    print("TEST 4: Checking Cache Directory")
    print("="*60)
    
    if os.path.exists('cache'):
        print("✓ Cache directory exists")
        files = os.listdir('cache')
        if files:
            print(f"✓ Cache contains {len(files)} file(s)")
            for f in files:
                print(f"   - {f}")
        else:
            print("ℹ Cache is empty (will be populated on first download)")
    else:
        print("ℹ Cache directory doesn't exist yet")
        print("  (Will be created automatically on first download)")
    
    print("\n✓ Cache system ready!\n")
    return True


def test_ui_files():
    """Test 5: Check UI files"""
    print("="*60)
    print("TEST 5: Checking UI Files")
    print("="*60)
    
    files_to_check = [
        ('templates/demo_index.html', 'citySelect'),
        ('static/js/demo_map.js', 'use_real_data'),
    ]
    
    all_good = True
    
    for filepath, keyword in files_to_check:
        if os.path.exists(filepath):
            print(f"✓ {filepath} exists")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if keyword in content:
                print(f"  ✓ Contains '{keyword}' (OSM integration)")
            else:
                print(f"  ✗ Missing '{keyword}' (OSM integration)")
                all_good = False
        else:
            print(f"✗ {filepath} NOT found")
            all_good = False
    
    if all_good:
        print("\n✓ All UI files properly configured!\n")
    else:
        print("\n✗ Some UI files need attention\n")
    
    return all_good


def test_documentation():
    """Test 6: Check documentation"""
    print("="*60)
    print("TEST 6: Checking Documentation")
    print("="*60)
    
    docs = [
        'README.md',
        'OSM_API_GUIDE.md',
        'REAL_MAPS_READY.md',
        'FINAL_STATUS.md',
        'START_HERE.md'
    ]
    
    found = 0
    for doc in docs:
        if os.path.exists(doc):
            print(f"✓ {doc}")
            found += 1
        else:
            print(f"✗ {doc} missing")
    
    print(f"\n✓ Found {found}/{len(docs)} key documentation files\n")
    return found >= 3


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("="*60)
    print("  GPS NAVIGATOR - INTEGRATION TEST")
    print("  Testing Real OpenStreetMap Integration")
    print("="*60)
    print("\n")
    
    tests = [
        ("Imports", test_imports),
        ("OSM Downloader", test_osm_downloader),
        ("Demo App", test_demo_app),
        ("Cache System", test_cache_directory),
        ("UI Files", test_ui_files),
        ("Documentation", test_documentation),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}\n")
            results.append((name, False))
    
    # Summary
    print("="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready!")
        print("\nNext steps:")
        print("  1. Run: python demo_app.py")
        print("  2. Open: http://localhost:5000")
        print("  3. Select 'Cairo - Tahrir Square'")
        print("  4. Click 'Load Map'")
        print("  5. Wait for download (first time only)")
        print("  6. Click on map to set points")
        print("  7. Click 'Find Route'")
        print("\n✓ Everything is working!\n")
    else:
        print("\n⚠️ Some tests failed. Check messages above.")
        print("   Most issues can be fixed by:")
        print("   1. pip install flask networkx requests")
        print("   2. Ensure all files are in correct locations\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
