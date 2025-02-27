# from django.test import TestCase
from datetime import datetime
import json

# Create your tests here.
_weekly_data = '''{
    "latitude": -1.875,
    "longitude": 30.125,
    "generationtime_ms": 0.5260705947875977,
    "utc_offset_seconds": 7200,
    "timezone": "Africa/Kigali",
    "timezone_abbreviation": "GMT+2",
    "elevation": 1519.0,
    "daily_units": {
        "time": "iso8601",
        "temperature_2m_max": "\u00b0C",
        "temperature_2m_min": "\u00b0C",
        "precipitation_sum": "mm",
        "weathercode": "wmo code",
        "sunrise": "iso8601",
        "sunset": "iso8601"
    },
    "daily": {
        "time": [
            "2025-01-23",
            "2025-01-24",
            "2025-01-25",
            "2025-01-26",
            "2025-01-27",
            "2025-01-28",
            "2025-01-29"
        ],
        "temperature_2m_max": [
            23.9,
            25.8,
            24.8,
            24.8,
            24.2,
            24.3,
            26.4
        ],
        "temperature_2m_min": [
            15.4,
            16.2,
            15.9,
            17.5,
            16.4,
            17.0,
            16.6
        ],
        "precipitation_sum": [
            2.2,
            1.1,
            3.1,
            6.0,
            24.3,
            8.4,
            0.9
        ],
        "weathercode": [
            95,
            3,
            95,
            96,
            95,
            96,
            3
        ],
        "sunrise": [
            "2025-01-23T06:05",
            "2025-01-24T06:05",
            "2025-01-25T06:05",
            "2025-01-26T06:06",
            "2025-01-27T06:06",
            "2025-01-28T06:06",
            "2025-01-29T06:06"
        ],
        "sunset": [
            "2025-01-23T18:17",
            "2025-01-24T18:17",
            "2025-01-25T18:17",
            "2025-01-26T18:18",
            "2025-01-27T18:18",
            "2025-01-28T18:18",
            "2025-01-29T18:18"
        ]
    }
}'''

_hourly_data = '''
{
    "coord": {
        "lon": -46.8528,
        "lat": -23.6495
    },
    "weather": [
        {
            "id": 804,
            "main": "Clouds",
            "description": "overcast clouds",
            "icon": "04d"
        }
    ],
    "base": "stations",
    "main": {
        "temp": 303.81,
        "feels_like": 304.05,
        "temp_min": 302.72,
        "temp_max": 304.17,
        "pressure": 1015,
        "humidity": 43,
        "sea_level": 1015,
        "grnd_level": 922
    },
    "visibility": 10000,
    "wind": {
        "speed": 3.2,
        "deg": 274,
        "gust": 3.88
    },
    "clouds": {
        "all": 100
    },
    "dt": 1737555599,
    "sys": {
        "type": 1,
        "id": 8446,
        "country": "BR",
        "sunrise": 1737535145,
        "sunset": 1737583120
    },
    "timezone": -10800,
    "id": 3464305,
    "name": "Embu",
    "cod": 200
}'''
hourly_data = json.loads(_hourly_data)
data = hourly_data.get('weather')[0].get('main')
print(data)


def simulate(h: bool = False, w: bool = False):
    # Process and format weather data
    weekly_data = json.loads(_weekly_data)
    hourly_data = json.loads(_hourly_data)
    weather_data = {
        "locName": hourly_data.get("name"),
        "country": hourly_data["sys"].get("country"),
        # Convert to Celsius
        "temperature": hourly_data["main"].get("temp") - 273.15,
        "icon": hourly_data["weather"][0].get("icon"),
        "visibility": hourly_data["visibility"],
        "feels_like": hourly_data["main"].get("feels_like") - 273.15,
        "humidity": hourly_data["main"].get("humidity"),
        "pressure": hourly_data["main"].get("pressure"),
        "wind_speed": hourly_data["wind"].get("speed"),
        "wind_direction": hourly_data["wind"].get("deg"),
        "weather_main": hourly_data["weather"][0].get("main"),
        "weather_description": hourly_data["weather"][0].get("description"),
        "rain_last_hour": hourly_data.get("rain", {}).get("1h", 0),
        "cloud_cover": hourly_data["clouds"].get("all"),
        "sunrise": datetime.fromtimestamp(hourly_data["sys"].get("sunrise")).strftime("%H:%M:%S"),
        "sunset": datetime.fromtimestamp(hourly_data["sys"].get("sunset")).strftime("%H:%M:%S"),
        "weekly": weekly_data,  # Weekly forecast data
    }
    if h:
        return hourly_data
    if w:
        return weekly_data
    return weather_data
