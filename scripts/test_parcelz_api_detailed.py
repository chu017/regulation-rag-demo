"""
Detailed test script for Parcelz property API integration.
This shows the actual API response for debugging.
"""
import json
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.parcelz_property_api import geocode_address_nominatim


def test_parcelz_api_detailed():
    """Test the Parcelz API with detailed output."""
    
    test_address = "123 Main St, San Francisco, CA 94102"
    
    print("=" * 60)
    print("Detailed Parcelz API Test")
    print("=" * 60)
    print()
    
    # Step 1: Geocode
    print("Step 1: Geocoding address...")
    print(f"Address: {test_address}")
    geocoded = geocode_address_nominatim(test_address)
    
    if not geocoded:
        print("[ERROR] Failed to geocode address")
        return
    
    print(f"[SUCCESS] Geocoded:")
    print(f"  Latitude: {geocoded['latitude']}")
    print(f"  Longitude: {geocoded['longitude']}")
    print(f"  Display Name: {geocoded.get('display_name', 'N/A')}")
    print()
    
    # Step 2: Call Parcelz API
    print("Step 2: Calling Parcelz API...")
    url = "https://app.parcel-z.com/api/v2/unidata/search/"
    # API requires exactly ONE of: (longitude+latitude), address, or apn
    params = {
        "longitude": str(geocoded["longitude"]),
        "latitude": str(geocoded["latitude"])
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("[SUCCESS] API Response:")
                print(json.dumps(data, indent=2))
            except:
                print("[WARNING] Response is not JSON:")
                print(response.text[:500])
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            try:
                error_data = response.json()
                print("Error Response:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Error Response (text):")
                print(response.text[:500])
                
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_parcelz_api_detailed()
