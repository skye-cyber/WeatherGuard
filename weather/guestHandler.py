from rest_framework.test import APIRequestFactory
from django.test.client import RequestFactory
from .models import CustomUser
from .email_templates import HourlyWeatherEmail, DailyWeatherEmail, WeeklyWeatherEmail
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
import logging
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from .weather import main as RetrieveWeatherData
# from django.test import RequestFactory
from django.http import JsonResponse


logger = logging.getLogger(__name__)


def getCoordinates(user, loc=False) -> str:
    locations = user.locations.all()  # Correct way to get related locations
    coordinates_list = [location.coordinates for location in locations]
    name_list = [location.name for location in locations]

    if not coordinates_list:
        # Handle empty lists safely
        raise ValueError("No locations found for this user.")

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
        email = request.data.get('email')

        user = CustomUser.objects.get(
            username=request.user)

        logger.info(f"\033[1mSending email to: \033[32m{email}\033[0m")
        coordinates = getCoordinates(user)
        weather_data = RetrieveWeatherData(coordinates, _type='hourly3')

        errors = None
        if not weather_data:
            errors = "Unable to obtain weather data."
        verbosity = user.verbosity.lower() if user.verbosity else "low"
        # Use HourlyWeatherEmail template (ensure this class exists in your templates)
        template = HourlyWeatherEmail()
        email_html = template.render(weather_data, verbosity)

        subject = "Your Hourly Weather Forecast from WeatherGuard"
        from_email = "WeatherGuard"
        recipient_list = [email] if email else [user.email]
        logger.info(user.email)
        email = EmailMultiAlternatives(
            subject, email_html, from_email, recipient_list)
        email.attach_alternative(email_html, "text/html")
        email.send(fail_silently=False)

        response_data = {
            "status": "success",
            "message": f"Hourly weather email sent to {[email] if email else [user.email]}.",
            "errors": errors,
        }
        logger.info(f"\033[1mSent to: \033[32m{email} Successfull\033[0m")
        return Response(response_data, status=HTTP_200_OK)


class SendDailyWeatherEmailsAPIView(APIView):
    """
    Sends weekly weather emails to all users who opted for weekly notifications.
    This view would ideally be triggered via a scheduled task.
    """
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        user = CustomUser.objects.get(
            username=request.user)

        logger.info(f"\033[1mSending email to: \033[32m{email}\033[0m")
        coordinates = getCoordinates(user)
        coordinates, loc_name = getCoordinates(user, loc=True)
        weather_data = RetrieveWeatherData(coordinates, _type='daily7')

        errors = None
        if not weather_data:
            errors = "Unable to obtain weather data."

        verbosity = user.verbosity.lower() if user.verbosity else "low"
        template = DailyWeatherEmail()
        email_html = template.render(weather_data, verbosity, loc_name)

        subject = "WeatherGuard Daily Weather Forecast"
        from_email = "WeatherGuard"
        recipient_list = [email] if email else [user.email]

        email = EmailMultiAlternatives(
            subject, email_html, from_email, recipient_list)
        email.attach_alternative(email_html, "text/html")
        email.send()

        response_data = {
            "status": "success",
            "message": f"Daily weather email sent to {[email] if email else [user.email]}.",
            "errors": errors,
        }
        logger.info(f"\033[1mSent to: \033[32m{email} Successfull\033[0m")
        return Response(response_data, status=HTTP_200_OK)


class SendWeeklyWeatherEmailsAPIView(APIView):
    """
    Sends weekly weather emails to all users who opted for weekly notifications.
    This view would ideally be triggered via a scheduled task.
    """
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        user = CustomUser.objects.get(
            username=request.user)

        logger.info(f"\033[1mSending email to: \033[32m{email}\033[0m")
        coordinates = getCoordinates(user)

        # Loop through the users, render the appropriate email content, and send the email.
        coordinates = getCoordinates(user)
        weather_data = RetrieveWeatherData(coordinates, _type='daily7')

        errors = None
        if not weather_data:
            errors = "Unable to obtain weather data."

        verbosity = user.verbosity.lower() if user.verbosity else "low"
        template = WeeklyWeatherEmail()
        email_html = template.render(weather_data, verbosity)

        subject = "WeatherGuard Weekly Weather Forecast"
        from_email = "WeatherGuard"
        recipient_list = [email] if email else [user.email]

        email = EmailMultiAlternatives(
            subject, email_html, from_email, recipient_list)
        email.attach_alternative(email_html, "text/html")
        email.send()

        response_data = {
            "status": "success",
            "message": f"Weekly weather email sent to {[email] if email else [user.email]}.",
            "errors": errors,
        }
        logger.info(f"\033[1mSent to: \033[32m{email} Successfull\033[0m")
        return Response(response_data, status=HTTP_200_OK)


class HandleNotifyNowAPI(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        print(f"\033[34m{request.data.get('email')}\033[0m")
        user = request.user
        logger.info(f"\033[1mEmail Request from: \033[32m{user}\033[0m")

        # Create a new DRF-compatible request using the parsed data.
        factory = APIRequestFactory()
        new_request = factory.post(
            request.path,
            data=request.data,  # Use already parsed data
            format='json'       # This ensures the data is JSON encoded
        )
        new_request.user = request.user
        new_request.META.update(request.META)

        # Delegate based on notification frequency
        if user.notification_frequency.lower() == "hourly":
            view = SendHourlyWeatherEmailAPIView.as_view()
            return view(new_request)
        elif user.notification_frequency.lower() == "daily":
            view = SendDailyWeatherEmailsAPIView.as_view()
            return view(new_request)
        elif user.notification_frequency.lower() == "weekly":
            view = SendWeeklyWeatherEmailsAPIView.as_view()
            return view(new_request)

        return Response({"detail": "No matching notification frequency."}, status=400)
