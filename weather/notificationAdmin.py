from .models import CustomUser
import pytz
from .email_templates import HourlyWeatherEmail, DailyWeatherEmail, WeeklyWeatherEmail
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
import datetime
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
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


def send_email(user, request):
    # Generate verification token and URL
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = reverse(
        'verify-email', kwargs={'uidb64': uid, 'token': token})
    verification_url = f"{get_current_site(request)}{verification_url}"
    verification_url = verification_url if verification_url.startswith(
        'https') else f'http://{verification_url}'
    logger.info(f"Verification URL: {verification_url}")

    subject = 'Verify your email'
    html_message = ""
    from_email = 'WeatherGuard'
    recipient_list = [user.email]
    email = EmailMessage(subject, html_message, from_email, recipient_list)
    email.content_subtype = "html"  # this is required because the default is text/plain
    email.send(fail_silently=False)


class SendHourlyWeatherEmailAPIView(APIView):
    """
    Sends hourly weather emails to all users who opted for hourly notifications.
    This view should be triggered via a scheduled task.
    """
    print("Start")
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        now = datetime.datetime.now(pytz.utc)
        logger.info(now)
        # Send weekly emails at intervals of 3hours from 06:00 UTC
        safeTimes = [2, 5, 6, 8, 9, 11]
        if now.hour not in safeTimes:
            pass
            # return Response({"status": "skipped", "message": "Not time to send weekly emails."}, status=HTTP_200_OK)
        # Retrieve users who opted in for hourly notifications
        hourly_users = CustomUser.objects.filter(
            notification_frequency="Hourly")
        errors = []
        successes = 0
        logger.info("Start loop")
        print("Start loop")
        for user in hourly_users:
            logger.info("User:", user)
            print("User:", user)
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
            print(user.email)
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
        print(response_data)
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
        if now.hour != 6:
            pass
            # return Response({"status": "skipped", "message": "Not time to send weekly emails."}, status=HTTP_200_OK)

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
        if now.weekday() != 0 or now.hour != 6:
            pass
            # return Response({"status": "skipped", "message": "Not time to send weekly emails."}, status=HTTP_200_OK)

        # Retrieve users who opted in for weekly notifications
        weekly_users = CustomUser.objects.filter(
            notification_frequency="Weekly")
        errors = []
        successes = 0
        print("Total user:", len(weekly_users))
        # Loop through the users, render the appropriate email content, and send the email.
        for user in weekly_users:
            print("-----user----:", user)
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
        print("Success!")
        logger.info(response_data)
        return Response(response_data, status=HTTP_200_OK)
