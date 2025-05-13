"""
API test script for The Dyrt scraper.
"""
import argparse
import json
import sys
import time

import requests

def test_api_endpoints(base_url="http://localhost:8000"):
    """
    Test the API endpoints.
    
    Args:
        base_url: Base URL of the API
    """
    print(f"Testing API endpoints at {base_url}")
    
    # Test root endpoint
    try:
        print("\n1. Testing root endpoint...")
        response = requests.get(f"{base_url}/")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test start scraper endpoint
    try:
        print("\n2. Testing start scraper endpoint...")
        response = requests.post(f"{base_url}/scrape")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test status endpoint
    try:
        print("\n3. Testing status endpoint...")
        response = requests.get(f"{base_url}/status")
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Wait for scraper to complete
    print("\nWaiting for scraper to complete (10 seconds)...")
    time.sleep(10)
    
    # Test campgrounds endpoint
    try:
        print("\n4. Testing campgrounds endpoint...")
        response = requests.get(f"{base_url}/campgrounds?limit=5")
        print(f"Status code: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} campgrounds")
        
        if len(data) > 0:
            print("\nSample campground:")
            print(json.dumps(data[0], indent=2))
            
            # Test specific campground endpoint
            campground_id = data[0]["id"]
            print(f"\n5. Testing specific campground endpoint for ID: {campground_id}...")
            response = requests.get(f"{base_url}/campgrounds/{campground_id}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test The Dyrt scraper API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    
    args = parser.parse_args()
    
    try:
        test_api_endpoints(base_url=args.url)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)