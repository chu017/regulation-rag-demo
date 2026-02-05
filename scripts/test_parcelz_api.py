"""
Test script for Parcelz property API integration.
Run this to verify the API is working correctly.
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.parcelz_property_api import get_property_info_from_address


def test_parcelz_api():
    """Test the Parcelz API with sample addresses."""
    
    # Test addresses (Bay Area)
    test_addresses = [
        "123 Main St, San Francisco, CA 94102",
        "456 Market St, Oakland, CA 94607",
        "789 First St, San Jose, CA 95110",
    ]
    
    print("=" * 60)
    print("Testing Parcelz Property API")
    print("=" * 60)
    print()
    
    for i, address in enumerate(test_addresses, 1):
        print(f"Test {i}: {address}")
        print("-" * 60)
        
        try:
            property_info = get_property_info_from_address(address)
            
            # Display results
            print(f"[SUCCESS]")
            print(f"   Address: {property_info.get('address', 'N/A')}")
            print(f"   City: {property_info.get('city', 'N/A')}")
            print(f"   Zoning: {property_info.get('zoning', 'N/A')}")
            print(f"   Lot Size: {property_info.get('lot_size_sqft', 'N/A')} sqft")
            print(f"   Existing Units: {property_info.get('existing_units', 'N/A')}")
            print(f"   Parcel ID: {property_info.get('parcel_id', 'N/A')}")
            print(f"   Latitude: {property_info.get('latitude', 'N/A')}")
            print(f"   Longitude: {property_info.get('longitude', 'N/A')}")
            
            # Show full JSON for debugging
            print("\n   Full JSON response:")
            print(json.dumps(property_info, indent=6))
            
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print()
    
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_parcelz_api()
