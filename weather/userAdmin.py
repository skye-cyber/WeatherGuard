from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, Location
from .serializers import LocationSerializer


class AddLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            location = serializer.save()
            request.user.user_locations.add(location)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationCreateView(generics.CreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Save the new location instance
        location = serializer.save()
        # Associate the location with the current user
        self.request.user.user_locations.add(location)


class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        new_password2 = request.data.get("new_password2")

        # Check that all required fields are provided.
        if not old_password or not new_password or not new_password2:
            return Response(
                {"error": "Please provide old_password, new_password, and new_password2."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify that the old password is correct.
        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify that the new passwords match.
        if new_password != new_password2:
            return Response(
                {"new_password": [
                    "The two new password fields didn't match."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Optionally, add your own password validation here.

        # Set the new password and save the user.
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)


class ResetPasswordEmailView(views.APIView):
    """
    Initiates a password reset process by sending a password reset email
    containing a link to the frontend reset password template.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # To avoid leaking which emails exist in the system,
            # always respond with the same message.
            return Response(
                {"detail": "If an account with this email exists, you will receive a password reset email."},
                status=status.HTTP_200_OK
            )

        # Generate a UID and token for the user.
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct the password reset URL.
        # Make sure to define FRONTEND_URL in your settings, e.g.,
        # FRONTEND_URL = "https://yourfrontend.com"
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Compose the email message.
        subject = "Password Reset Request"
        message = (
            f"Hi {user.username},\n\n"
            f"Please click the link below to reset your password:\n{reset_url}\n\n"
            "If you did not request a password reset, please ignore this email."
        )
        from_email = settings.DEFAULT_FROM_EMAIL

        # Send the email.
        send_mail(subject, message, from_email, [
                  user.email], fail_silently=False)

        return Response(
            {"detail": "If an account with this email exists, you will receive a password reset email."},
            status=status.HTTP_200_OK
        )
