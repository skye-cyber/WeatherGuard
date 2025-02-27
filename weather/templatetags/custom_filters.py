# weather/templatetags/custom_filters.py
import logging
import re
from datetime import datetime, date
from django import template

register = template.Library()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug('Custom template tags loaded')


@register.filter(namr='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(namr='get_percent')
def get_percent(obj):
    return obj * 100


@register.filter(name='get_dp')
def get_dp(val):
    return f"{val:.2f}"


@register.filter(name='get_desc')
def get_weather_description(weather_code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        4: r"75-100% cloudy",
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

    code = weather_codes.get(weather_code, "Unknown weather code")
    if code == "Unknown weather code":
        validCode = validate_and_extract_code(weather_code)
        code = weather_codes.get(validCode, "Unknown weather code")
    return code


def validate_and_extract_code(code):
    # Define the regex pattern to match the code in the form 'XXd'
    pattern = r'^(\d{2})d$'

    # Use re.match to check if the code matches the pattern
    match = re.match(pattern, code)

    if match:
        # Extract the numeric part
        numeric_part = match.group(1)
        return int(numeric_part)  # Convert to integer if needed
    else:
        return None  # Return None if the code does not match the pattern


@register.filter
def get_icon(val):
    icon_dict = {
        "Clear sky": 'clear-sky.png',
        "Mainly clear": 'mainly-clear.png',
        "Partly cloudy": 'partly-cloudy.png',
        r"75-100% cloudy": 'overcast.png',
        "Overcast": 'overcast.png',
        "Fog": 'fog.png',
        "Freezing fog": 'freezing-fog.png',
        "Drizzle (light)": 'lightdrizzles.png',
        "Drizzle (moderate)": 'moderatedrizzles.png',
        "Drizzle (heavy)": 'drizzles.png',
        "Rain (light)": 'light-rain.png',
        "Rain (moderate)": 'moderate-rain.png',
        "Rain (heavy)": 'heavy-rain.png',
        "Snow (light)": 'lightsnow.png',
        "Snow (moderate)": 'snow.png',
        "Snow (heavy)": 'snow.png',
        "Rain showers (light)": 'showerslight.png',
        "Rain showers (moderate)": 'showers.png',
        "Rain showers (heavy)": 'showers.png',
        "Snow showers (light)": 'snowshowers.png',
        "Snow showers (heavy)": 'snowshowers.png',
        "Thunderstorm (light)": 'thunderstorm.png',
        "Thunderstorm with hail (light)": 'thubdertormM.png',
        "Thunderstorm (heavy)": 'thunderstorm.png'
    }
    return icon_dict.get(val)


@register.filter
def get_index(data, value):
    """Returns the index of 'value' in 'data'."""
    try:
        return data[value]
    except ValueError:
        return 'Index out of range'  # Or handle as needed


@register.filter
def find_index(data, value):
    """Returns the index of 'value' in 'data'."""
    try:
        val_index = [index for (index, val) in enumerate(data) if val == value][0]
        return val_index
    except ValueError:
        return 'Index out of range'  # Or handle as needed


@register.filter(name='today_date')
def DateToday(val=None):
    date_object = date.today().strftime('%Y-%m-%d')
    return date_object


@register.filter
def get_day(date_string):

    # Convert the string to a datetime object
    date_object = datetime.strptime(date_string, "%Y-%m-%d")

    # Get the day of the week (0=Monday, 6=Sunday)
    day_of_week = date_object.weekday()

    # Alternatively, get the ISO weekday (1=Monday, 7=Sunday)
    # iso_day_of_week = date_object.isoweekday()
    day_dict = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    # Print results
    # print(f"The day of the week for {date_string} is: {day_of_week}: {day_dict.get(day_of_week)}")
    # print(f"The ISO weekday for {date_string} is: {iso_day_of_week} (1=Monday, 7=Sunday)")
    return day_dict.get(day_of_week)


@register.filter
def toTitle(string: str) -> str:
    return string.title()


@register.filter
def normal_time(datetime_string):
    # Convert the string to a datetime object
    datetime_object = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M")

    # Format the datetime object into a more readable format
    formatted_time = datetime_object.strftime(
        "%I:%M %p")  # Example: "2024-10-31 06:20 PM"

    # Print the formatted time
    # print(f"The formatted time is: {formatted_time}")
    return formatted_time
