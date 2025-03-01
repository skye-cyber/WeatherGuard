import time
import os
import json
import geopy.exc as geo
from pathlib import Path
import requests
import logging
from geopy.geocoders import Geocodio, GoogleV3, Nominatim, OpenCage
from .WGCrypto.CryptoAdmin import OPCA, LIQA

# API keys for fallback services
OPENCAGE_API_KEY = OPCA()
# GOOGLE_API_KEY = "your_google_api_key"
LOCATIONIQ_API_KEY = LIQA()
# GEOCODIO_API_KEY = "your_geocodio_api_key"

logger = logging.getLogger(__name__)


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

    def ConstructPath(self, loc=None):
        loc = self.city_name.lower() if not loc else loc
        cache_file = f'{loc.lower()}.json'
        cache_dir = os.path.join(Path(__file__).parent, 'cache', 'loc')
        os.makedirs(cache_dir, exist_ok=True)
        fpath = os.path.join(cache_dir, cache_file)
        if not fpath:
            return None
        return fpath

    def FetchCache(self, loc: str = None) -> str:
        fpath = self.ConstructPath()

        if fpath and os.path.exists(fpath):
            with open(fpath, 'r') as f:
                data = json.load(f)
            lat = data.get('coordinates')['lat']
            lon = data.get('coordinates')['lon']
            return [lat, lon]
        return None

    def WriteCache(self, lat, lon) -> bool:
        fpath = self.ConstructPath()
        logger.info(
            f"Writing \033[34m{lat}\033[0m, \033[34m{lon}\033[0m to \033[33m{fpath}\033[0m")

        # Check that fpath is valid.
        if not fpath:
            logger.error("Invalid file path!")
            return False

        data = {"coordinates": {"lat": lat, "lon": lon}}

        try:
            with open(fpath, 'w') as fp:
                json.dump(data, fp, indent=4)
            logger.info('\033[1;32mSuccess!\033[0m')
            return True
        except Exception as e:
            logger.error(f"Failed to write cache: {e}")
            return False

    def Control(self):
        cache_coord = self.FetchCache()

        if cache_coord:
            print("Return cache_coord")
            return cache_coord

        # Attempt with each geopy-supported geocoder
        for name, geolocator in self.geolocators:
            coordinates = self.attempt_geocode(geolocator, name)
            print("coord", coordinates)
            if coordinates:
                self.WriteCache(coordinates[0], coordinates[1])
                if self.string:
                    return f"{coordinates[0]}, {coordinates[1]}"
                return coordinates
            print(f"Falling back from {name}.")

        # Attempt LocationIQ last
        coordinates = self.locationiq_geocode()
        if coordinates:
            self.WriteCache(coordinates[0], coordinates[1])
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
