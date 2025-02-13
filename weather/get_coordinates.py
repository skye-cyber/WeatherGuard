import time

import geopy.exc as geo
import requests
from geopy.geocoders import Geocodio, GoogleV3, Nominatim, OpenCage

# API keys for fallback services
OPENCAGE_API_KEY = "9c54a5cc9cbe449199aa4b3922f8e7ad"
# GOOGLE_API_KEY = "your_google_api_key"
LOCATIONIQ_API_KEY = "pk.e4d47e2a0ef858ff977567a91af035eb"
# GEOCODIO_API_KEY = "your_geocodio_api_key"


def get_latitude_longitude(city_name, retries: int = 3):
    geolocators = [
        ("Nominatim", Nominatim(user_agent="unique_application_name", timeout=10)),
        ("OpenCage", OpenCage(api_key=OPENCAGE_API_KEY, timeout=10))
        # ("GoogleV3", GoogleV3(api_key=GOOGLE_API_KEY, timeout=10)),
        # ("Geocodio", Geocodio(api_key=GEOCODIO_API_KEY, timeout=10))
    ]

    def attempt_geocode(geolocator, name):
        for attempt in range(1, retries + 1):
            try:
                print(f"Attempt {attempt} with {name}")
                location = geolocator.geocode(city_name)
                if location:
                    return location.latitude, location.longitude
                time.sleep(1.5)
            except geo.GeocoderTimedOut:
                print(f"{name} service timed out.")
            except geo.GeocoderQuotaExceeded:
                print(f"{name} quota exceeded.")
                return None
        return None

    # Attempt with each geopy-supported geocoder
    for name, geolocator in geolocators:
        coordinates = attempt_geocode(geolocator, name)
        if coordinates:
            return coordinates
        print(f"Falling back from {name}.")

    # LocationIQ as a manual fallback
    def locationiq_geocode(city_name):
        url = f"https://us1.locationiq.com/v1/search?key={LOCATIONIQ_API_KEY}&q={city_name}&format=json&"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except requests.exceptions.RequestException as e:
            print(f"LocationIQ error: {e}")
        return None

    # Attempt LocationIQ last
    coordinates = locationiq_geocode(city_name)
    if coordinates:
        return coordinates

    print("All geocoding services failed.")
    return None


if __name__ == "__main__":
    url = f"https://us1.locationiq.com/v1/search?key={LOCATIONIQ_API_KEY}&q=Wajir&format=json&"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        if data:
            print(float(data[0]["lat"]), float(data[0]["lon"]))
    except requests.exceptions.RequestException as e:
        print(f"LocationIQ error: {e}")
