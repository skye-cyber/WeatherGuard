import time

import geopy.exc as geo
import requests
from geopy.geocoders import Geocodio, GoogleV3, Nominatim, OpenCage

# API keys for fallback services
OPENCAGE_API_KEY = "9c54a5cc9cbe449199aa4b3922f8e7ad"
# GOOGLE_API_KEY = "your_google_api_key"
LOCATIONIQ_API_KEY = "pk.e4d47e2a0ef858ff977567a91af035eb"
# GEOCODIO_API_KEY = "your_geocodio_api_key"


class CoordAdmin:
    def __init__(self, city_name, retries: int = 3,  string=False):
        self.city_name = city_name
        self.retries = retries
        self.string = string
        geolocators = [
            ("Nominatim", Nominatim(user_agent="unique_application_name", timeout=10)),
            ("OpenCage", OpenCage(api_key=OPENCAGE_API_KEY, timeout=10))
            # ("GoogleV3", GoogleV3(api_key=GOOGLE_API_KEY, timeout=10)),
            # ("Geocodio", Geocodio(api_key=GEOCODIO_API_KEY, timeout=10))
        ]
        self.geolocators = geolocators

    def attempt_geocode(self, geolocator, name):
        for attempt in range(1, self.retries + 1):
            try:
                print(f"Attempt {attempt} with {name}, {self.city_name}")
                location = geolocator.geocode(self.city_name)
                if location:
                    print(location)
                    return location.latitude, location.longitude
                time.sleep(1.5)
            except geo.GeocoderTimedOut:
                raise
                print(f"{name} service timed out.")
            except geo.GeocoderQuotaExceeded:
                raise
                print(f"{name} quota exceeded.")
                return None
        return None

    # LocationIQ as a manual fallback

    def locationiq_geocode(self):
        url = f"https://us1.locationiq.com/v1/search?key={LOCATIONIQ_API_KEY}&q={self.city_name}&format=json&"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except requests.exceptions.RequestException as e:
            print(f"LocationIQ error: {e}")
        return None

    def Control(self):
        # Attempt with each geopy-supported geocoder
        for name, geolocator in self.geolocators:
            coordinates = self.attempt_geocode(geolocator, name)
            print("coord", coordinates)
            if coordinates:
                if self.string:
                    return f"{coordinates[0]}, {coordinates[1]}"
                return coordinates
            print(f"Falling back from {name}.")

        # Attempt LocationIQ last
        coordinates = self.locationiq_geocode()
        if coordinates:
            if self.string:
                return f"{coordinates[0]}, {coordinates[1]}"
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
