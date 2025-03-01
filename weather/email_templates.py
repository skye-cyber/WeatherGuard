from datetime import date
from .templatetags import custom_filters


class WeatherEmailTemplate:
    """Abstract base class for weather email templates."""

    def render(self, weather_data, verbosity):
        raise NotImplementedError("Subclasses must implement this method.")


class HourlyWeatherEmail(WeatherEmailTemplate):
    def render(self, weather_data, verbosity):
        humidity = weather_data.get('main').get('humidity')
        temp = weather_data.get('main').get('temp') - 273.15
        temp_max = weather_data.get('main').get('temp_max') - 273.15
        temp_min = weather_data.get('main').get('temp_min') - 273.15
        pressure = weather_data.get('main').get('pressure')
        feels_like = weather_data.get('main').get("feels_like") - 273.15
        sea_level = weather_data.get('main').get('sea_level')
        ground_level = weather_data.get('main').get('grnd_level')
        Location = weather_data.get('name')
        sunrise = weather_data.get('sys').get('sunrise')
        sunset = weather_data.get('sys').get('sunset')
        country = weather_data.get('sys').get('country')
        cound_cover = weather_data.get('clouds').get('all')
        wind_speed = weather_data.get('wind').get('speed')
        wind_direction = weather_data.get('wind').get('deg')
        weather = weather_data.get('weather')[0].get('main')
        weather_desc = wind_direction = weather_data.get('weather')[0].get('description')
        visibility = wind_direction = weather_data.get('visibility')

        if verbosity == 'low':
            content = f"""
            <section style="display: flex; justify-content: center; padding: 20px; background-color: #f4f4f4;">
                <div style="font-family: Arial, sans-serif; color: #333; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); max-width: 400px; text-align: left;">
                    <h1 style="color: #2c7be5; margin-bottom: 10px;">🌤 Hourly Weather Update</h1>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌡 Temperature:</strong> {temp:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌥 Main Weather:</strong> {weather} - {weather_desc}</p>
                </div>
            </section>

            """
        elif verbosity == 'medium':
            content = f"""
            <section style="display: flex; justify-content: center; padding: 20px; background-color: #f4f4f4;">
                <div style="font-family: Arial, sans-serif; color: #333; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); max-width: 450px; text-align: left;">
                    <h1 style="color: #2c7be5; margin-bottom: 10px;">🌤 Hourly Weather Update</h1>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌡 Temperature:</strong> {temp:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🤔 Feels Like:</strong> {feels_like:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌥 Weather:</strong> {weather} - {weather_desc}</p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>💨 Wind Speed:</strong> {wind_speed} <span style="color: #0055ff;">m/s</span></p>
                </div>
            </section>

            """
        elif verbosity == 'high':
            content = f"""
            <section style="display: flex; justify-content: center; padding: 20px; background-color: #f4f4f4;">
                <div style="font-family: Arial, sans-serif; color: #333; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); max-width: 500px; text-align: left;">
                    <h1 style="color: #2c7be5; margin-bottom: 10px;">Hourly Weather Update</h1>
                    <p style="margin: 5px 0;"><strong>📍 Location:</strong> {Location}, {country}</p>
                    <p style="margin: 5px 0;"><strong>🌡 Temperature:</strong> {temp:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0;"><strong>🤔 Feels Like:</strong> {feels_like:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0;"><strong>💧 Humidity:</strong> {humidity}<span style="color: #0055ff;">%</span></p>
                    <p style="margin: 5px 0;"><strong>🌀 Pressure:</strong> {pressure} <span style="color: #0055ff;">hPa</span></p>
                    <p style="margin: 5px 0;"><strong>👀 Visibility:</strong> {visibility} <span style="color: #0055ff;">m</span></p>
                    <p style="margin: 5px 0;"><strong>💨 Wind:</strong> {wind_speed} <span style="color: #0055ff;">m/s</span> | <strong>⬆ Direction:</strong> {wind_direction}°</p>
                    <p style="margin: 5px 0;"><strong>🌤 Weather:</strong> {weather} - {weather_desc}</p>
                    <p style="margin: 5px 0;"><strong>☁ Cloud Cover:</strong> {cound_cover}<span style="color: #0055ff;">%</span></p>
                </div>
            </section>

            """
        else:
            content = "<p>Invalid verbosity level.</p>"
        return content


class DailyWeatherEmail(WeatherEmailTemplate):

    def render(self, weather_data, verbosity, loc=""):
        # Unbundle data
        date_object = date.today().strftime('%Y-%m-%d')
        # Extract daily forecast data from weather_data
        daily = weather_data.get("daily", {})
        times = weather_data.get('daily', [])['time']
        index = [index for (index, val) in enumerate(times) if val == date_object][0]
        temp_max_list = daily['temperature_2m_max']
        temp_min_list = daily['temperature_2m_min']
        precip_list = daily['precipitation_sum']
        weathercode_list = daily['weathercode']
        timezone = weather_data.get('timezone')
        sunrise_list = daily['sunrise']
        sunset_list = daily['sunset']

        # Build each row for the table
        date_OBJ = times[index]
        temp_max = temp_max_list[index] if index < len(temp_max_list) else "N/A"
        temp_min = temp_min_list[index] if index < len(temp_min_list) else "N/A"
        precip = precip_list[index] if index < len(precip_list) else "N/A"
        sunrise = sunrise_list[index] if index < len(sunrise_list) else "N/A"
        sunset = sunset_list[index] if index < len(sunset_list) else "N/A"
        weathercode = weathercode_list[index] if index <= len(weathercode_list) else "N/A"
        weather_main = custom_filters.get_weather_description(weathercode)
        temp_avg = (int(temp_max)+int(temp_min))/2

        # Base content includes sunrise/sunset information
        if verbosity == 'low':
            content = f"""
            <section style="display: flex; justify-content: center; padding: 20px; background-color: #f4f4f4;">
                <div style="font-family: Arial, sans-serif; color: #333; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); max-width: 450px; text-align: center;">
                    <h1 style="color: #28a745; margin-bottom: 10px;">🌞 Daily Weather Update</h1>
                    <h3 style="color: #1447ff; margin-bottom: 10px;">{custom_filters.get_day(date_OBJ).title()} - {date_OBJ}</h3>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌡 Temperature:</strong> {temp_avg:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌅 Sunrise:</strong> {custom_filters.normal_time(sunrise)} | <strong>🌇 Sunset:</strong> {custom_filters.normal_time(sunset)}</p>
                </div>
            </section>

            """
        elif verbosity == 'medium':
            content = f"""
            <section style="display: flex; justify-content: center; padding: 20px; background-color: #f4f4f4;">
                <div style="font-family: Arial, sans-serif; color: #333; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); max-width: 450px; text-align: center;">
                    <h1 style="color: #28a745; margin-bottom: 10px;">🌞 Daily Weather Update</h1>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌡 Average Temperature:</strong> {temp_avg:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🔥 Maximum Temperature:</strong> {temp_max:.2f}<span style="color: #ff5733;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>❄ Minimum Temperature:</strong> {temp_min:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌅 Sunrise:</strong> {custom_filters.normal_time(sunrise)} | <strong>🌇 Sunset:</strong> {custom_filters.normal_time(sunset)}</p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>☁ Weather:</strong> {weather_main}</p>
                </div>
            </section>

            """
        elif verbosity == 'high':
            content = f"""
            <section style="display: flex; justify-content: center; padding: 20px; background-color: #f4f4f4;">
                <div style="font-family: Arial, sans-serif; color: #333; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); max-width: 500px; text-align: center;">
                    <h1 style="color: #28a745; margin-bottom: 10px;">🌞 Daily Weather Update</h1>
                    <h3 style="margin: 10px 0;"><strong>📍 Location:</strong> {loc.title()} | <strong>⏳ Timezone:</strong> {timezone.title()}</h3>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌡 Temperature:</strong> {temp_avg:.2f}<span style="color: #0055ff;">°C</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌧 Precipitation:</strong> {precip} <span style="color: #0055ff;">mm</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>💧 Humidity:</strong> N/A<span style="color: #0055ff;">%</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌀 Pressure:</strong> N/A<span style="color: #0055ff;"> hPa</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>👀 Visibility:</strong> N/A<span style="color: #0055ff;"> m</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>💨 Wind:</strong> N/A m/s, N/A<span style="color: #0055ff;">°</span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>☁ Weather:</strong> <span style="color: #ff007f;"><strong>{weather_main}</strong></span></p>
                    <p style="margin: 5px 0; font-size: 16px;"><strong>🌅 Sunrise:</strong> {custom_filters.normal_time(sunrise)} | <strong>🌇 Sunset:</strong> {custom_filters.normal_time(sunset)}</p>
                </div>
            </section>
            """
        else:
            content = "<p>Invalid verbosity level.</p>"
        return content


class WeeklyWeatherEmail:
    """
    Renders a weekly weather forecast email using daily forecast data.
    The forecast is displayed in a table whose columns vary by verbosity.
    """

    def render(self, weather_data, verbosity):
        # Extract daily forecast data from weather_data
        daily = weather_data.get("daily", {})
        times = daily.get("time", [])
        temp_max_list = daily.get("temperature_2m_max", [])
        temp_min_list = daily.get("temperature_2m_min", [])
        precip_list = daily.get("precipitation_sum", [])
        sunrise_list = daily.get("sunrise", [])
        sunset_list = daily.get("sunset", [])
        main_weather_list = daily.get('weathercode', [])

        forecast_items = ""
        # Build each row for the table
        for i in range(len(times)):
            date = times[i]
            temp_max = temp_max_list[i] if i < len(temp_max_list) else "N/A"
            temp_min = temp_min_list[i] if i < len(temp_min_list) else "N/A"
            precip = precip_list[i] if i < len(precip_list) else "N/A"
            sunrise = sunrise_list[i] if i < len(sunrise_list) else "N/A"
            sunset = sunset_list[i] if i < len(sunset_list) else "N/A"
            main_weather = main_weather_list[i] if i < len(main_weather_list) else "N/A"

            if verbosity == "low":
                forecast_items += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><span style="color: #00a3ef;">{custom_filters.get_day(date)}</span>-{date}</td>
                     <td style="padding: 8px; border: 1px solid #ddd;">{custom_filters.get_weather_description(main_weather)}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{temp_max}°C / {temp_min}°C</td>
                </tr>
                """
            elif verbosity == "medium":
                forecast_items += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><span style="color: #00a3ef;">{custom_filters.get_day(date)}</span>-{date}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{custom_filters.get_weather_description(main_weather)}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{temp_max}<span style="color: #0055ff;">°C</span> / {temp_min}<span style="color: #0055ff;">°C</span></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">Precip: {precip} <span style="color: #0055ff;">mm</span></td>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Sunrise</strong>: {custom_filters.normal_time(sunrise)}<br>Sunset: {custom_filters.normal_time(sunset)}</td>
                </tr>
                """
            elif verbosity == "high":
                forecast_items += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        <span style="color: #00a3ef; font-weight: bold;">{custom_filters.get_day(date).title()}</span> - {date}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        {custom_filters.get_weather_description(main_weather)}
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        <span style="color: #ff654a; font-weight: bold;">High:</span> {temp_max}°C<br>
                        <span style="color: #5bc0de; font-weight: bold;">Low:</span> {temp_min}°C
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        <span style="color: #0055ff;">Precipitation:</span> {precip} mm
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">
                        <strong style="font-weight: bold;">Sunrise:</strong> {custom_filters.normal_time(sunrise)}<br>
                        <strong style="font-weight: bold;">Sunset:</strong> {custom_filters.normal_time(sunset)}
                    </td>
                </tr>

                """
            else:
                forecast_items += "<tr><td colspan='4'>Invalid verbosity level.</td></tr>"

        # Table header depends on verbosity
        if verbosity == "low":
            header = """
            <tr>
                <th style="padding: 8px; border: 1px solid #ddd;">Date</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Main Weather</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Temp (High/Low)</th>
            </tr>
            """
        elif verbosity in ["medium", "high"]:
            header = """
            <tr>
                <th style="padding: 8px; border: 1px solid #ddd;">Date</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Main Weather</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Temperature</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Precipitation</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Sunrise / Sunset</th>
            </tr>
            """
        else:
            header = "<tr><td>Invalid verbosity level.</td></tr>"

        table = f"""
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            {header}
            {forecast_items}
        </table>
        """

        content = f"""
        <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
            <h1 style="color: #d63384; text-align: center;">Weekly Weather Forecast</h1>
            <p style="text-align: center;">Here is your forecast for the upcoming week:</p>
            {table}
        </div>
        """
        return content
