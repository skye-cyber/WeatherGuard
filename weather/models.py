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
        related_name='customuser_set',  # Renamed to avoid conflict
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Renamed to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    user_locations = models.ManyToManyField(  # Renamed to avoid conflict
        'Location',
        related_name='users',  # Specify a unique related_name
        blank=True,
        verbose_name='locations',
    )

    def is_fully_verified(self):
        return self.email_verified or self.phone_verified

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
    user = models.ForeignKey(
        # Renamed to avoid conflict
        CustomUser, on_delete=models.CASCADE, related_name='location_set', default=1)
    name = models.CharField(max_length=255)
    coordinates = models.CharField(max_length=255)

    def __str__(self):
        return self.name
