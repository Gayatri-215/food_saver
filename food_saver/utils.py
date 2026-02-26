import math
from datetime import timedelta
from django.utils import timezone

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def predict_expiry(food_type, preparation_time):
    """
    AI-based expiry prediction (simulated ML logic).
    Predicts the safety duration based on food type and preparation time.
    """
    # Base durations in hours
    expiry_rules = {
        'veg': 12,        # Standard vegetarian food
        'non-veg': 6,     # Non-vegetarian food expires faster
        'bakery': 48,     # Breads and cakes last longer
        'fruits': 72,     # Fresh fruits
    }
    
    # Get base duration for the food type (default to 6 hours for safety)
    duration_hours = expiry_rules.get(food_type.lower(), 6)
    
    # Simple "Environmental factor" - assume shorter duration if it's currently hot (simulated)
    # real ML would take temp/humidity as inputs
    
    return preparation_time + timedelta(hours=duration_hours)
