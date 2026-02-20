from geopy.geocoders import Nominatim


def get_coordinates(address: str):
    geolocator = Nominatim()

    try:
        location = geolocator.geocode(address)
        if location:
            return location.adress, location.latitude, location.longitude
        return None, None, None
    except Exception:
        return None, None, None
