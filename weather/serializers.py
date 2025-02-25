from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import CustomUser, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'coordinates']


class CustomUserSerializer(serializers.ModelSerializer):
    # Using a different name for clarity
    locations = LocationSerializer(many=True, required=False)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone',
                  'password1', 'password2', 'locations',
                  'verbosity', 'notification_frequency', 'notification_medium',]
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True}
        }

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError(
                {'password2': 'Passwords must match.'})
        return data

    def create(self, validated_data):
        password1 = validated_data.pop('password1')
        validated_data.pop('password2', None)
        locations_data = validated_data.pop('locations', [])

        # Create user first
        user = CustomUser.objects.create_user(
            password=password1, **validated_data)
        user.save()  # Ensure the user is saved before linking locations

        # Now, create or get each location and associate with the user
        for location_data in locations_data:
            location, created = Location.objects.get_or_create(
                name=location_data['name'],
                coordinates=location_data['coordinates']
            )
            user.user_locations.add(location)

        return user
