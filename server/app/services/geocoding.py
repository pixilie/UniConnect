from geopy.geocoders import Nominatim


def get_coordinates(address: str) -> tuple[str, float, float] | tuple[None, None, None]:
    geolocator = Nominatim(user_agent="uniconnect_app")

    try:
        location = geolocator.geocode(address)

        if location:
            return location.address, location.latitude, location.longitude

        return None, None, None

    except Exception:
        return None, None, None
