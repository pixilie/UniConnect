from geopy.geocoders import Nominatim


def get_coordinates(address: str):
    geolocator = Nominatim(user_agent="uniconnect_app")

    try:
        location = geolocator.geocode(address)
        print("aaaaaa")
        if location:
            print(location.address, location.latitude, location.longitude)
            return location.address, location.latitude, location.longitude
        return None, None, None
    except Exception:
        return None, None, None
