from django.contrib.auth import authenticate, login
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
import logging
import random
import json
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core import exceptions
from django.core.mail import EmailMessage
# from django.db.models import QuerySet
from django.http import (HttpResponseForbidden, HttpResponseRedirect,
                         JsonResponse, StreamingHttpResponse)
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest
from django.core.handlers.wsgi import WSGIRequest
from .get_coordinates import CoordAdmin
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer
from .weather import main
from django.template.loader import render_to_string

User = get_user_model()

logger = logging.getLogger(__name__)


def get_login(request):
    return render(request, 'registration/login.html')


def get_register(request):
    return render(request, 'registration/register.html')


def get_verification(request):
    user_email = request.session.get('user_email', None)
    return render(request, "registration/verify.html", {'user_email': user_email})


@api_view(['GET'])
@permission_classes([AllowAny])
def geocode_location(request):
    location = request.GET.get('loc_name')

    if not location:
        return Response({'error': 'Location is required'}, status=400)

    Coordadmin = CoordAdmin(location)
    coord = Coordadmin.Control()
    if not coord:
        return Response({'error': 'Coordinates not found'}, status=404)

    # Convert the tuple to a list
    coord_list = list(coord)

    return Response({'coordinates': coord_list})


@login_required
def get_home(request):
    content = get_weatherData(request)
    context = {"weather_data_dict": content}
    # logger.info(f"Got---{content}")
    if not content:
        return render(request, 'index.html')
    elif isinstance(content, str):
        return render(request, 'index.html', {"error_messages": content})
    return render(request, 'index.html', context)


@permission_classes([IsAuthenticated])
class SearchLocation(APIView):
    def post(self, request, *args, **kwargs):
        # ✅ Save request body **before** DRF reads it
        # Use the cached body instead of request.body
        raw_body = getattr(request, '_cached_body', b'')

        # ✅ Clone the Django WSGIRequest with the same properties
        django_request = WSGIRequest(request._request.environ)  # Convert DRF request to Django request
        django_request.method = request.method
        django_request._body = raw_body  # Restore original body
        django_request.META = request.META

        location = request.data.get('loc_name')

        Coordadmin = CoordAdmin(location)
        coord = Coordadmin.Control()

        if not coord:
            return Response({'error': 'Coordinates not found'}, status=404)

        coord_list = list(coord)

        logger.info(f"\033[1mCoord_Search Results: \033[1;33m{coord_list}\033[0m")

        content = get_weatherData(django_request, coord_list)

        context = {"weather_data_dict": content}

        if not context or isinstance(context, str):
            return JsonResponse({'status': 'error', 'code': 401}, status=401)

        # Render the entire index.html template to a string.
        rendered_html = render_to_string('index.html', context, request=request)
        return JsonResponse({
            "status": "success", "html": rendered_html})


@api_view(["POST"])
@permission_classes([AllowAny])
@csrf_exempt  # Disable CSRF check
def guest_login_api(request):
    """
    API to log in a guest user.
    """
    guest_username = "Guest101"
    guest_password = "weatherGuardGuest"

    user = authenticate(username=guest_username, password=guest_password)
    if user is not None:
        login(request, user)
        # token, created = Token.objects.get_or_create(user=user)  # Get or create auth token

        return JsonResponse({
            'status': 'success',
            'code': 200,
            "message": "Logged in as Guest!",
            # "username": user.username,
            # "token": token.key
        }, status=200)
    else:
        return JsonResponse({"error": "Guest login failed."}, status=400)


@permission_classes([AllowAny])
class SendSMSVerificationCodeView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        print(phone_number)
        if not phone_number:
            logger.error(
                "Phone number is required for sending SMS verification code.")
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a 6-digit verification code
        verification_code = str(random.randint(100000, 999999))
        logger.info(f"Generated verification code: {verification_code}")

        # Send the verification code via SMS
        client = Client(settings.TWILIO_ACCOUNT_SID,
                        settings.TWILIO_AUTH_TOKEN)
        try:
            """message = client.messages.create(
                body=f'Your weatherguard verification code is: {verification_code}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )"""
            verification = client.verify.v2.services(
                "VAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").verifications.create(
                channel="sms",
                custom_friendly_name='WeatherGuard',
                custom_message=f'Your weatherguard verification code is: {verification_code}',
                # from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number)

            logger.info(
                f"SMS sent successfully. Message SID: {verification.status}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return Response({'error': 'Failed to send verification code'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save the verification code in the session or database for later verification
        request.session['verification_code'] = verification_code
        logger.info(f"Verification code saved in session: {verification_code}")

        return Response({'message': 'Verification code sent successfully'}, status=status.HTTP_200_OK)


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
    html_message = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; }}
            .header {{ text-align: center; }}
            .message {{ margin-bottom: 20px; }}
            .button-container {{ text-align: center; }}
            .button {{ background-color: #007BFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .footer {{ text-align: center; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Verify your email</h1>
            </div>
            <div class="message">
                <p>Dear {user.username},</p>
                <p>Thank you for registering! To activate your account, please click the button below:</p>
            </div>
            <div class="button-container">
                <a href="{verification_url}" target="_blank" class="button">Verify Email</a>
            </div>
            <p>Alternatively click: <a href="{verification_url}">{verification_url}</a></p>
            <div class="footer">
                <p>If you did not make this request, please ignore this email.</p>
                <p>Best regards,<br>The skye-cyber Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    from_email = 'WeatherGuard'
    recipient_list = [user.email]
    email = EmailMessage(subject, html_message, from_email, recipient_list)
    email.content_subtype = "html"  # this is required because the default is text/plain
    email.send(fail_silently=False)


@permission_classes([AllowAny])
class RegisterAPIView(APIView):
    renderer_classes = [JSONRenderer]  # Force JSON responses

    def post(self, request, *args, **kwargs):
        # return Response({'errors':errors}, status=HTTP_400_BAD_REQUEST)
        # logger.info(f"Received POST request with data: {request.data}")

        # Extract location data from request
        location_name = request.data.get('location_name')
        location_coordinates = request.data.get('location_coordinates')

        # Prepare data for serializer
        data = {
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'phone': request.data.get('phone'),
            'password1': request.data.get('password1'),
            'password2': request.data.get('password2'),
            'locations': [
                {'name': location_name, 'coordinates': location_coordinates}
            ] if location_name and location_coordinates else []
        }

        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            send_email(user, request)  # Call the send_email function
            # Store the email in the session for later use
            request.session['user_email'] = data['email']

            # Return JSON success response instead of redirecting
            return Response({'status': 'success', 'redirect_url': reverse('verification_page')}, status=200)
        logger.error(f"Serializer errors: {serializer.errors}")
        return Response({'errors': serializer.errors}, status=HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class ResendEmailAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # if request.data.get('email') else user.email
        email = request.data.get('email')
        if not email:
            email = request.session.get('user_email', None)
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
    if request.method == 'POST':
        # Handle the form submission to send the SMS verification code
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            logger.error(
                "Phone number is required for sending SMS verification code.")
            return render(request, 'egistration/verify.html', {'error': 'Phone number is required'})

        # Make a POST request to the SendSMSVerificationCodeView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.post(
            '/send-sms-verification-code/', {'phone_number': phone_number})
        response = SendSMSVerificationCodeView.as_view()(request)

        if response.status_code == 200:
            return render(request, 'registration/verify_pending.html')
        else:
            return render(request, 'registration/login.html', {'error': response.data.get('error')})

    # If GET request, try to use the user's phone number (if logged in)
    phone_number = request.user.phone if request.user.is_authenticated else None

    if phone_number:
        print("Got GET request")
        # Make a POST request to the SendSMSVerificationCodeView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.post(
            '/send-sms-verification-code/', {'phone_number': phone_number})
        response = SendSMSVerificationCodeView.as_view()(request)

        if response.status_code == 200:
            return render(request, 'registration/verify_phone.html')
        else:
            return render(request, 'registration/login.html', {'error': response.data.get('error')})
    else:
        return redirect('login')


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


@permission_classes([AllowAny])
class VerifySMSView(APIView):
    def post(self, request, *args, **kwargs):
        entered_code = request.data.get('verification_code')
        expected_code = request.session.get('verification_code')

        if not entered_code:
            logger.error("Verification code is required.")
            return Response({'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not expected_code:
            logger.error("No verification code found in session.")
            return Response({'error': 'No verification code found in session'}, status=status.HTTP_400_BAD_REQUEST)

        if entered_code == expected_code:
            # Verification successful
            # Remove the verification code from the session
            request.session.pop('verification_code', None)
            logger.info("Verification successful.")
            return Response({'message': 'Verification successful'}, status=status.HTTP_200_OK)
        else:
            # Verification failed
            logger.error("Incorrect verification code.")
            return Response({'error': 'Incorrect verification code'}, status=status.HTTP_400_BAD_REQUEST)


def verification_form(request):
    return render(request, 'registration/verify_phone.html')


# @ratelimit(key='ip', rate='5/m', method='ALL', block=True)

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['username'], password=cd['password'])

            try:
                user = CustomUser.objects.get(username=cd["username"])
            except CustomUser.DoesNotExist:
                messages.error(request, 'User does not exist.')
                return render(request, 'registration/login.html', {'form': form})

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home') if user.email_verified or user.phone_verified else redirect('await-verification')
                else:
                    messages.error(request, 'Account is disabled❌')
            else:
                messages.error(request, 'Incorrect login credentials')

        # If form is invalid, return it with errors
        return render(request, 'registration/login.html', {'form': form})

    # GET request - return a blank form
    else:
        form = AuthenticationForm()
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


def get_weatherData(request, coord_search: str = None) -> dict:
    if not coord_search:
        locations = request.user.user_locations.filter(users=request.user)
        coordinates_list = [location.coordinates for location in locations]
        if not coordinates_list:
            return "User has not set locations!"
        # Get all locations from the database or source
        # Ensure this function returns a list of locations
        coord = coordinates_list[0]
        lat, lon = coord.split(',')
    else:
        lat, lon = coord_search
        coord = f"{lat}, {lon}"

    print("lat:", lat, "lon:", lon)

    RetrieveErrors = []

    try:
        # Retrieve weather data for the current location
        weekly_data = main(coord)
        hourly_data = main(coord, _type='hourly3')

        # Check for API errors
        if isinstance(weekly_data, str) and weekly_data in ("RequestFailure", "ConnectionError"):
            RetrieveErrors.append({"location": coord, "error": weekly_data})

        if isinstance(hourly_data, str) and hourly_data in ("RequestFailure", "ConnectionError"):
            RetrieveErrors.append({"location": coord, "error": hourly_data})
        if not (weekly_data and hourly_data):
            return f'{weekly_data}_{hourly_data}'

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

    except Exception as e:
        # Log errors for debugging
        raise
        logger.error(e)
        # JsonResponse({'status': 'status', 'code': 500}, status=500)
        return f'Failed to obtain location data: {e}'

    return weather_data
