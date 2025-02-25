import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(
        default=uuid.uuid4, null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Avoids conflict with default User.groups
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Avoids conflict with default User.user_permissions
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    user_locations = models.ManyToManyField(
        'Location',
        related_name='users',  # Now you can access all users related to a location
        blank=True,
        verbose_name='locations',
    )

    # Define choices for preferences
    VERBOSITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    NOTIFICATION_FREQUENCY_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    NOTIFICATION_MEDIUM_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
    ]

    # Add preference fields with defaults
    verbosity = models.CharField(
        max_length=10,
        choices=VERBOSITY_CHOICES,
        default='medium'
    )
    notification_frequency = models.CharField(
        max_length=10,
        choices=NOTIFICATION_FREQUENCY_CHOICES,
        default='daily'
    )
    notification_medium = models.CharField(
        max_length=10,
        choices=NOTIFICATION_MEDIUM_CHOICES,
        default='email'
    )

    def is_fully_verified(self):
        return self.email_verified or self.phone_verified

    @property
    def locations(self):
        return self.user_locations.all()

    def __str__(self):
        return self.username


# accounts/models.py


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    verification_token = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Create a signal to create a Profile when a User is created


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Location(models.Model):
    name = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.coordinates})"


"""
@receiver(post_save, sender=CustomUser)
def create_default_location(sender, instance, created, **kwargs):
    if created:  # Only run when a new user is created
        Location.objects.create(user=instance, name="Default Location", coordinates="0,0")
"""
