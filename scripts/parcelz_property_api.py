"""
Property API integration using Parcelz to get city, zoning, and parcel attributes from an address.
Replaces the placeholder property_api.py with actual Parcelz API integration.
"""
import requests
import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_property_info_from_address(address: str) -> Dict:
    """
    Get property information from an address using Parcelz API.
    
    The Parcelz API requires longitude and latitude, so we first geocode the address,
    then query Parcelz with the coordinates.
    
    Args:
        address: Property address string
    
    Returns:
        Dict with property information:
        - city: City name
        - zoning: Zoning code
        - lot_size_sqft: Lot size in square feet
        - existing_units: Number of existing units
        - parcel_id: Parcel identifier
        - address: Normalized address
        - latitude: Latitude coordinate
        - longitude: Longitude coordinate
    """
    try:
        # Step 1: Geocode address to get coordinates
        geocoded = geocode_address_nominatim(address)
        
        if not geocoded or not geocoded.get("latitude") or not geocoded.get("longitude"):
            print(f"Warning: Could not geocode address: {address}. Using fallback.")
            return _get_placeholder_property_info(address)
        
        latitude = geocoded["latitude"]
        longitude = geocoded["longitude"]
        
        # Step 2: Query Parcelz API with coordinates
        # Based on the Express.js code: https://app.parcel-z.com/api/v2/unidata/search/
        # Note: API requires exactly ONE of: (longitude+latitude), address, or apn
        url = "https://app.parcel-z.com/api/v2/unidata/search/"
        
        # Use coordinates (not address) as per API requirement
        params = {
            "longitude": str(longitude),
            "latitude": str(latitude)
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        # Check response status
        if response.status_code != 200:
            error_msg = f"Parcelz API returned status {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f": {error_data}"
            except:
                error_msg += f": {response.text[:200]}"
            print(f"Warning: {error_msg}. Using fallback.")
            return _get_placeholder_property_info(address)
        
        data = response.json()
        
        # Handle null response (no property found at coordinates)
        if data is None:
            print(f"Warning: Parcelz API returned null (no property found). Using fallback.")
            return _get_placeholder_property_info(address)
        
        # Parse Parcelz API response
        # The response structure may vary - adjust based on actual API response
        property_info = _parse_parcelz_response(data, address, latitude, longitude)
        
        return property_info
        
    except requests.exceptions.RequestException as e:
        print(f"Warning: Parcelz API error: {e}. Using fallback.")
        return _get_placeholder_property_info(address)
    except Exception as e:
        print(f"Warning: Error processing Parcelz response: {e}. Using fallback.")
        return _get_placeholder_property_info(address)


def _parse_parcelz_response(data: Dict, address: str, latitude: float, longitude: float) -> Dict:
    """
    Parse Parcelz API response into standardized property info format.
    
    Adjust field mappings based on actual Parcelz API response structure.
    """
    # Common field name variations - adjust based on actual response
    property_info = {
        "address": data.get("address") or data.get("formatted_address") or address,
        "city": (
            data.get("city") or 
            data.get("city_name") or 
            data.get("municipality") or
            _extract_city_from_address(address)
        ),
        "zoning": (
            data.get("zoning") or 
            data.get("zoning_code") or 
            data.get("zoning_classification") or
            "Unknown"
        ),
        "lot_size_sqft": (
            data.get("lot_size_sqft") or 
            data.get("lot_size") or 
            data.get("lot_area_sqft") or
            data.get("lot_area") or
            0
        ),
        "existing_units": (
            data.get("existing_units") or 
            data.get("units") or 
            data.get("number_of_units") or
            data.get("unit_count") or
            1
        ),
        "parcel_id": (
            data.get("parcel_id") or 
            data.get("apn") or 
            data.get("assessor_parcel_number") or
            data.get("fid") or
            "Unknown"
        ),
        "latitude": latitude,
        "longitude": longitude
    }
    
    # Add any additional fields from Parcelz response
    # Common additional fields that might be useful:
    if "property_type" in data:
        property_info["property_type"] = data["property_type"]
    if "year_built" in data:
        property_info["year_built"] = data["year_built"]
    if "square_feet" in data or "sqft" in data:
        property_info["building_sqft"] = data.get("square_feet") or data.get("sqft")
    if "bedrooms" in data:
        property_info["bedrooms"] = data["bedrooms"]
    if "bathrooms" in data:
        property_info["bathrooms"] = data["bathrooms"]
    
    return property_info


def _get_placeholder_property_info(address: str) -> Dict:
    """
    Fallback implementation when Parcelz API is unavailable.
    Returns only real data extracted from address (city, coordinates).
    """
    address_lower = address.lower()
    
    # Simple city extraction (Bay Area cities)
    bay_area_cities = [
        "san francisco", "oakland", "san jose", "berkeley", "palo alto",
        "mountain view", "sunnyvale", "fremont", "hayward", "santa clara",
        "redwood city", "san mateo", "burlingame", "millbrae", "daly city"
    ]
    
    city = None
    for city_name in bay_area_cities:
        if city_name in address_lower:
            city = city_name.title()
            break
    
    if not city:
        city = "Unknown"
    
    # Return only real data - no placeholder values
    property_info = {
        "address": address,
        "city": city,
        "zoning": None,
        "lot_size_sqft": None,
        "existing_units": None,
        "parcel_id": None,
        "latitude": None,
        "longitude": None
    }
    
    # Try geocoding to get coordinates
    geocoded = geocode_address_nominatim(address)
    if geocoded:
        property_info["latitude"] = geocoded.get("latitude")
        property_info["longitude"] = geocoded.get("longitude")
    
    return property_info


def _extract_city_from_address(address: str) -> str:
    """Extract city name from address string."""
    address_lower = address.lower()
    
    bay_area_cities = [
        "san francisco", "oakland", "san jose", "berkeley", "palo alto",
        "mountain view", "sunnyvale", "fremont", "hayward", "santa clara",
        "redwood city", "san mateo", "burlingame", "millbrae", "daly city"
    ]
    
    for city_name in bay_area_cities:
        if city_name in address_lower:
            return city_name.title()
    
    return "Unknown"


def geocode_address_nominatim(address: str) -> Optional[Dict]:
    """
    Geocode address using OpenStreetMap Nominatim (free, no API key needed).
    This is used to get coordinates for Parcelz API lookup.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "Regulation-RAG-Demo/1.0"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                result = data[0]
                lat = result.get("lat")
                lon = result.get("lon")
                
                if lat and lon:
                    return {
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "display_name": result.get("display_name", "")
                    }
    except Exception as e:
        print(f"Geocoding error: {e}")
    
    return None


if __name__ == "__main__":
    # Test
    test_address = "123 Main St, San Francisco, CA 94102"
    info = get_property_info_from_address(test_address)
    print(json.dumps(info, indent=2))
