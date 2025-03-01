from .models import CustomUser
import pytz
from .email_templates import HourlyWeatherEmail, DailyWeatherEmail, WeeklyWeatherEmail
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
import datetime
import logging
from rest_framework.renderers import JSONRenderer
from .weather import main as RetrieveWeatherData


logger = logging.getLogger(__name__)


def getCoordinates(user, loc=False) -> str:
    locations = user.locations.all()  # Correct way to get related locations
    coordinates_list = [location.coordinates for location in locations]
    name_list = [location.name for location in locations]

    if not coordinates_list:
        raise ValueError("No locations found for this user.")  # Handle empty lists safely

    if loc:
        return coordinates_list[0], name_list[0]
    return coordinates_list[0]  # Returns the first location's coordinates


class SendHourlyWeatherEmailAPIView(APIView):
    """
    Sends hourly weather emails to all users who opted for hourly notifications.
    This view should be triggered via a scheduled task.
    """
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        now = datetime.datetime.now(pytz.utc)
        logger.info(now)

        # Send weekly emails at intervals of 3hours from 06:00 UTC
        safeTimes = [2, 5, 8, 11, 14, 17]  # Only send notifications at [0200hrs, 0500hrs, 0800hrs, 1100hrs, 1400hrs, 1700hrs]
        if now.hour not in safeTimes:
            return Response({"status": "skipped", "message": "Not time to send weekly emails."}, status=HTTP_200_OK)

        # Retrieve users who opted in for hourly notifications
        hourly_users = CustomUser.objects.filter(
            notification_frequency="Hourly")

        errors = []
        successes = 0
        logger.info("Start loop")
        for user in hourly_users:
            logger.info("User:", user)
            coordinates = getCoordinates(user)
            weather_data = RetrieveWeatherData(coordinates, _type='hourly3')
            if not weather_data:
                errors.append(
                    f"Weather data not available for user {user.email}")
                continue  # Skip this user and continue with the next

            verbosity = user.verbosity.lower() if user.verbosity else "low"
            # Use HourlyWeatherEmail template (ensure this class exists in your templates)
            template = HourlyWeatherEmail()
            email_html = template.render(weather_data, verbosity)

            subject = "Your Hourly Weather Forecast from WeatherGuard"
            from_email = "WeatherGuard"
            recipient_list = [user.email]
            logger.info(user.email)
            email = EmailMultiAlternatives(
                subject, email_html, from_email, recipient_list)
            email.attach_alternative(email_html, "text/html")
            email.send(fail_silently=False)
            successes += 1

        response_data = {
            "status": "success",
            "message": f"Hourly weather emails sent to {successes} users.",
            "errors": errors,
        }
        logger.info(response_data)
        return Response(response_data, status=HTTP_200_OK)


class SendDailyWeatherEmailsAPIView(APIView):
    """
    Sends weekly weather emails to all users who opted for weekly notifications.
    This view would ideally be triggered via a scheduled task.
    """
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        now = datetime.datetime.now(pytz.utc)

        # Send daily emails only at 06:00 UTC
        if now.hour != 5:  # Only send notification at 8AM
            return Response({"status": "skipped", "message": "Not time to send weekly emails."}, status=HTTP_200_OK)

        # Retrieve users who opted in for weekly notifications
        daily_users = CustomUser.objects.filter(
            notification_frequency="Daily")
        errors = []
        successes = 0

        # Loop through the users, render the appropriate email content, and send the email.
        for user in daily_users:
            coordinates, loc_name = getCoordinates(user, loc=True)
            weather_data = RetrieveWeatherData(coordinates, _type='daily7')
            if not weather_data:
                errors.append(
                    f"Weather data not available for user {user.email}")
                continue  # Skip this user and continue with the next
            verbosity = user.verbosity.lower() if user.verbosity else "low"
            template = DailyWeatherEmail()
            email_html = template.render(weather_data, verbosity, loc_name)

            subject = "WeatherGuard Daily Weather Forecast"
            from_email = "WeatherGuard"
            recipient_list = [user.email]

            email = EmailMultiAlternatives(
                subject, email_html, from_email, recipient_list)
            email.attach_alternative(email_html, "text/html")
            email.send()
            successes += 1

        response_data = {
            "status": "success",
            "message": f"Daily weather emails sent to {successes} users.",
            "errors": errors,
        }
        logger.info(response_data)
        return Response(response_data, status=HTTP_200_OK)


class SendWeeklyWeatherEmailsAPIView(APIView):
    """
    Sends weekly weather emails to all users who opted for weekly notifications.
    This view would ideally be triggered via a scheduled task.
    """
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        now = datetime.datetime.now(pytz.utc)

        # Send weekly emails only on Mondays at 06:00 UTC
        if now.weekday() != 5 or now.hour != 5:  # Only send notification at 8AM on Friday
            return Response({"status": "skipped", "message": "Not time to send weekly emails."}, status=HTTP_200_OK)

        # Retrieve users who opted in for weekly notifications
        weekly_users = CustomUser.objects.filter(
            notification_frequency="Weekly")
        errors = []
        successes = 0
        logger.info("Total user:", len(weekly_users))
        # Loop through the users, render the appropriate email content, and send the email.
        for user in weekly_users:
            logger.info(f"\033[1mSending to user: \033[33m{user}\033[0m")
            coordinates = getCoordinates(user)
            weather_data = RetrieveWeatherData(coordinates, _type='daily7')
            if not weather_data:
                errors.append(
                    f"Weather data not available for user {user.email}")
                continue  # Skip this user and continue with the next
            verbosity = user.verbosity.lower() if user.verbosity else "low"
            template = WeeklyWeatherEmail()
            email_html = template.render(weather_data, verbosity)

            subject = "WeatherGuard Weekly Weather Forecast"
            from_email = "WeatherGuard"
            recipient_list = [user.email]

            email = EmailMultiAlternatives(
                subject, email_html, from_email, recipient_list)
            email.attach_alternative(email_html, "text/html")
            email.send()
            successes += 1

        response_data = {
            "status": "success",
            "message": f"Weekly weather emails sent to {successes} users.",
            "errors": errors,
        }
        logger.info("Success!")
        logger.info(response_data)
        return Response(response_data, status=HTTP_200_OK)
