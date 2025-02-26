import configparser
import json
import os
import platform
from datetime import datetime
# import time
from pathlib import Path
import requests

# from django.conf import settings
from .get_coordinates import CoordAdmin

# Create a configuration object
config = configparser.ConfigParser()


class Weather:
    def __init__(self, coord):
        self.coord = coord

        def getCOORD():
            try:
                self.lat, self.lon = coord.split(',')
            except Exception as e:
                print(e)

        getCOORD()

    def get_daily_forecast(self):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={
            self.lat}&longitude={self.lon}&current_weather=true"

        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return "ConnectionError"
        except Exception as e:
            print(e)
            return "RequestFailure"

        if response.status_code == 200:
            data = response.json()
            with open("test.json", "w"):
                json.dump(data, indent=4)
            return data["current_weather"]
        else:
            return None

    def get_weekly_forecast(self, cache_file):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={self.lat}&longitude={
            self.lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode,sunrise,sunset&timezone=auto"

        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            return "ConnectionError"
        except Exception as e:
            print(e)
            return "RequestFailure"

        if response.status_code == 200:
            data = response.json()
            if not os.path.exists(os.path.dirname(cache_file)):
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            if not os.path.isfile(cache_file):
                parent_dir = os.path.dirname(cache_file)
                if not os.access(parent_dir, os.W_OK):  # Check access permission
                    raise PermissionError(
                        f"[Perm] Cannot write to the parent directory '{parent_dir}'"
                    )
            try:
                with open(str(cache_file), "w") as fp:
                    json.dump(data, fp, indent=4)
            except Exception as e:
                print(f"Error saving to cache file '{cache_file}'. {e}")
            return data
        else:
            return None

    @staticmethod
    def get_weather_description(weather_code):
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Freezing fog",
            51: "Drizzle (light)",
            53: "Drizzle (moderate)",
            55: "Drizzle (heavy)",
            61: "Rain (light)",
            63: "Rain (moderate)",
            65: "Rain (heavy)",
            71: "Snow (light)",
            73: "Snow (moderate)",
            75: "Snow (heavy)",
            80: "Rain showers (light)",
            81: "Rain showers (moderate)",
            82: "Rain showers (heavy)",
            85: "Snow showers (light)",
            86: "Snow showers (heavy)",
            95: "Thunderstorm (light)",
            96: "Thunderstorm with hail (light)",
            99: "Thunderstorm (heavy)",
        }

        return weather_codes.get(weather_code, "Unknown weather code")

    def _3hrs_forecast(self, path):
        api_key = "d1fce76f166b700e091ab7848af756db"

        # weather_root = settings.MEDIA_ROOT

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={
            self.lat}&lon={self.lon}&appid={api_key}"

        try:
            response = requests.get(url, timeout=None)
        except requests.exceptions.ConnectionError:
            return "ConnectionError"
        except Exception as e:
            print(e)
            return "RequestFailure"

        if response.status_code == 200:
            weather_data = response.json()

            # json_file = os.path.join(weather_root, filename)

            with open(path, "w") as json_file:
                json.dump(weather_data, json_file, indent=4)

            print(f"Data saved to {path}")

            return weather_data
        else:
            return None


def main(coord_str, loc_n=None, _type: str = "daily7", max_attempts: bool = 5):
    date = datetime.now().strftime("%Y-%m-%d")
    if _type == "daily7":
        filename = f"weatherCache/weekly_{loc_n.lower()}_{date}.json"
        cache_file = os.path.join(Path(__file__).parent, filename)
        if os.path.exists(cache_file):
            print(f"Loading data from daily7 file {cache_file}")
            with open(cache_file, "r") as file:
                return json.load(file)

        else:
            init = Weather(coord_str)
            forecast = init.get_weekly_forecast(cache_file)

    elif _type == "hourly3":
        filename = f"weatherCache/horly3_{loc_n.lower()}_{date}.json"
        cache_file = os.path.join(Path(__file__).parent, filename)
        if os.path.exists(cache_file):
            print(f"Loading data from horly3 file {cache_file}")
            with open(cache_file, "r") as json_file:
                return json.load(json_file)
        else:
            init = Weather(coord_str)
            forecast = init._3hrs_forecast(cache_file)

    if forecast:
        return forecast
    else:
        print("Unable to retrieve forecast.")
        return None


if __name__ == "__main__":
    url = "https://api.open-meteo.com/v1/forecast?latitude=-23.625&longitude=-46.875&current_weather=true"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
        print("*" * 100)
        with open("test.json", "w") as fl:
            json.dump(data, fl, indent=4)
        print(data["current_weather"])

    """forecast = main("Nairobi")
    forecast = forecast['daily']
    if forecast:
        for day in forecast['time']:
            index = forecast['time'].index(day)
            desc = Weather.get_weather_description(forecast['weathercode'][index])
            print(f"Date: {day}")
            print(f"Max Temperature: {forecast['temperature_2m_max'][index]}°C")
            print(f"Min Temperature: {forecast['temperature_2m_min'][index]}°C")
            print(f"Precipitation: {forecast['precipitation_sum'][index]} mm")
            print(f"Weather Code: {forecast['weathercode'][index]} {desc}")
            print(f"Sunrise: {forecast['sunrise'][index]}")
            print(f"Sunset: {forecast['sunset'][index]}")
            print("-" * 30)
    else:
        print("Failed to retrieve weather data.")"""
