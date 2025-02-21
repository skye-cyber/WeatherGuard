from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core import exceptions
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect,
                         JsonResponse, StreamingHttpResponse)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django_ratelimit.decorators import ratelimit
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client
from .forms import CustomRegistrationForm
from .get_coordinates import get_latitude_longitude
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer
from .weather import main
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def get_login(request):
    return render(request, 'registration/login.html')


def get_register(request):
    return render(request, 'registration/register.html')


def get_verification(request):
    render(request, "verify.html")


@api_view(['GET'])
def geocode_location(request):
    location = request.GET.get('loc_name')
    if not location:
        return Response({'error': 'Location is required'}, status=400)

    coord = get_latitude_longitude(location)
    if not coord:
        return Response({'error': 'Coordinates not found'}, status=404)

    # Convert the tuple to a list
    coord_list = list(coord)

    return Response({'coordinates': coord_list})


@login_required
def get_home(request):
    context = get_weatherData(request)
    if not context:
        return render(request, 'index.html')
    elif isinstance(context, str):
        print("context", context)
        return render(request, 'index.html', {"error_messages": context})
    return render(request, 'index.html', context)


def send_email(user, request):
    # Generate verification token and URL
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_url = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    verification_url = f"{get_current_site(request)}{verification_url}"
    logger.info(f"Verification URL: {verification_url}")

    send_mail(
        'Verify your email',
        f'Please click the link to verify your email: {verification_url}',
        'skye17@gmail.com',
        [user.email],
        fail_silently=False,
    )


class RegisterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.info(f"Received POST request with data: {request.data}")
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_email(user, request)  # Call the send_email function
            messages.success(request, 'Registration successful! Please verify your email to activate your account.')
            return redirect('await-verification')
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendEmailAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            logger.error("Email is required for resending verification.")
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.error(f"No user found with email: {email}")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        send_email(user, request)  # Reuse the send_email function
        messages.success(request, 'Verification email resent successfully.')
        return JsonResponse({'message': 'Verification email resent successfully.'}, status=status.HTTP_200_OK)


def verification_pending(request):
    return render(request, 'registration/verify.html')


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        messages.success(
            request, 'Your email has been verified. You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Verification link is invalid.')
        return redirect('onboard')


# @ratelimit(key='ip', rate='5/m', method='ALL', block=True)
def user_login(request):
    """if getattr(request, 'limited', False):
        return HttpResponseForbidden('Rate limit exceeded')"""

    if request.method == "POST":
        # Instantiate the form with submitted data
        form = AuthenticationForm(request, data=request.POST)

        # Check wether the form is valid
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['username'], password=cd['password'])

            # Check if the user exists
            try:
                user = CustomUser.objects.get(username=cd["username"])
            except CustomUser.DoesNotExist:
                messages.error(request, 'User does not exist.')
                return render(request, 'registration/login.html', {'form': form})

            # User exists
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # messages.success(request, f'Welcome, {cd["username"]}. You are now logged in.')
                    if user.email_verified or user.phone_verified:
                        return redirect('home')
                    return redirect('await-verification')

                else:
                    messages.error(request, 'Account is disabled❌')
            else:
                messages.error(request, 'Incorrect login credentials')
        else:
            messages.error(request, 'Invalid username or password.')

    # When the user_login view is submitted via GET request a new login form is Instantiated with for = LoginForm() to display it in the template.
    else:
        # form = LoginForm()
        form = AuthenticationForm()
    print(form.errors)
    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return HttpResponseRedirect(reverse('userlogin'))


def GetLocationDetail(request, name=False, coord=False):
    """
    Fetch farm details for the currently logged-in user.
    If no flags (name or coord) are provided, return all data in dictionary form.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    # Fetch the user's profile
    user_profile = Profile.objects.filter(user=request.user)
    """for loc in user_profile:
        print(loc.__dict__)"""
    if not user_profile.exists():
        return JsonResponse({'error': 'No locations found for the user'}, status=404)

    if not name and not coord:
        # Return all data in dictionary form
        all_data = [loc.__dict__ for loc in user_profile]
        for loc_data in all_data:
            loc_data.pop('_state', None)
        return JsonResponse(all_data, safe=False)

    try:
        # Determine the field to retrieve based on the flag
        field = 'location_coordinates' if coord else 'location_name'
        # Retrieve the specific field data
        data = user_profile.values_list(field, flat=True)
    except exceptions.FieldError:
        return None

    return JsonResponse(list(data), safe=False)


def get_weatherData(request):
    # Get all locations from the database or source
    # Ensure this function returns a list of locations
    locations = GetLocationDetail(request, coord=True)
    locNames = GetLocationDetail(request, name=True)
    weather_data_list = []
    error_locations = []

    # Fetch weather data for each location
    if locations:
        for loc, locName in zip(locations, locNames):
            try:
                # Retrieve weather data for the current location
                weekly_data = main(loc)
                hourly_data = main(loc, _type='hourly3')

                # Check for API errors
                if isinstance(weekly_data, str) and weekly_data in ("RequestFailure", "ConnectionError"):
                    error_locations.append(
                        {"location": loc, "error": weekly_data})
                    continue
                if isinstance(hourly_data, str) and hourly_data in ("RequestFailure", "ConnectionError"):
                    error_locations.append(
                        {"location": loc, "error": hourly_data})
                    continue

                # Process and format weather data
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

                # Append processed data to the list
                weather_data_list.append(weather_data)

            except Exception as e:
                # Log errors for debugging
                raise
                error_locations.append({"location": loc, "error": str(e)})

        # Render the data in the template
        context = {
            "weather_data_list": weather_data_list
        }
        if error_locations and weather_data_list == []:
            # render(request, 'index.html', {"error_message": error_locations}, status=404)
            return "error obtaining weather data!"
        return context
    else:
        # render(request, 'index.html', {'error_message': 'User has not set locations!'}, status=404)
        return "User has not set locations!"


def send_sms(message):
    account_sid = 'YOUR_TWILIO_ACCOUNT_SID'
    auth_token = 'YOUR_TWILIO_AUTH_TOKEN'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_='YOUR_TWILIO_PHONE_NUMBER',
        to='RECIPIENT_PHONE_NUMBER'
    )
    return message.sid


class WeatherView(View):
    def get(self, request):
        api_key = 'YOUR_API_KEY'
        city = 'Your_City'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
        response = requests.get(url)
        data = response.json()
        return JsonResponse(data)


class WeatherNotificationView(View):
    def get(self, request):
        weather_data = requests.get(
            'http://api.openweathermap.org/data/2.5/weather?q=Your_City&appid=YOUR_API_KEY').json()
        weather_description = weather_data.get(
            'weather', [{}])[0].get('description', '')
        if 'rain' in weather_description.lower():
            message = "It's going to rain today. Don't forget your umbrella!"
            send_sms(message)
            return JsonResponse({'status': 'Notification sent'})
        else:
            return JsonResponse({'status': 'No rain forecasted'})
