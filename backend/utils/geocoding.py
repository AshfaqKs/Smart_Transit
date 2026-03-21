"""
Geocoding Utility — SmartTransit
Handles reverse geocoding to convert coordinates to human-readable names.
"""
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

# Initialize Nominatim Geocoder with a custom user-agent
geocoder = Nominatim(user_agent="smart_transit_app")

# Simple in-memory cache to avoid redundant API calls
# Key: (rounded_lat, rounded_lng), Value: location_name
_geo_cache = {}

def get_location_name(lat, lng):
    """
    Reverse geocodes (lat, lng) to a location name.
    Uses rounding to 4 decimal places (~11m precision) for caching.
    """
    if lat is None or lng is None:
        return None

    try:
        # Round to 4 decimal places for caching (approx 11 meters)
        f_lat = float(lat)
        f_lng = float(lng)
        key = (round(f_lat, 4), round(f_lng, 4))
        if key in _geo_cache:
            return _geo_cache[key]

        # Call Nominatim API
        location = geocoder.reverse(f"{f_lat}, {f_lng}", language='en')
        if location:
            # Try to get a concise name (suburb, city, or road)
            address = location.raw.get('address', {})
            name = (
                address.get('suburb') or 
                address.get('neighbourhood') or 
                address.get('city_district') or 
                address.get('town') or 
                address.get('village') or 
                address.get('road') or
                address.get('county') or
                location.address.split(',')[0]
            )
            
            # Find a parent that is more general than the current name
            # We look for city, then state_district (often the main district like Ernakulam)
            city = address.get('city')
            district = address.get('state_district')
            
            parent = None
            if city and city.lower() != name.lower():
                parent = city
            elif district and district.lower() != name.lower():
                parent = district

            if parent:
                name = f"{name}, {parent}"

            _geo_cache[key] = name
            return name
            
    except (GeocoderTimedOut, GeocoderServiceError, Exception) as e:
        print(f"[GEO] Geocoding error: {e}")
        
    return None
