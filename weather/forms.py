from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import CustomUser, Location


class CustomRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. 30 characters or fewer. Letters, digits, and @/./+/-/_ only.'
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Inform a valid email address.'
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$', message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed.")]
    )
    location_name = forms.CharField(
        label='Location Name',
        max_length=100,
        required=True,
        error_messages={
            'required': 'This field is required.',
            'invalid': 'Please enter a valid city or location.'
        }
    )

    password1 = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    password2 = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    location_coordinates = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',
                  'phone', 'location_name', 'location_coordinates',
                  'locations')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_location_name(self):
        location_name = self.cleaned_data.get('location_name')
        if not location_name:
            raise ValidationError('Location name cannot be empty.')
        return location_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # User is not active until verified
        location_name = self.cleaned_data.get('location_name')
        location_coordinates = self.cleaned_data.get('location_coordinates')

        if commit:
            user.save()
            location, created = Location.objects.get_or_create(
                name=location_name, coordinates=location_coordinates)
            user.locations.add(location)
            for loc in self.cleaned_data.get('locations', []):
                user.locations.add(loc)
        return user


class LoginForm(forms.Form):
    username = forms.CharField(required=True,)
    password = forms.CharField(widget=forms.PasswordInput, required=True,)
