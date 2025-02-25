from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomRegistrationForm
from .models import CustomUser, Location

# Custom User Admin


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'verbosity', 'notification_frequency', 'notification_medium', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',
                         'user_locations')  # Include our M2M field here

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser', 'groups', 'user_permissions')}),
        ('Preferences', {'fields': ('verbosity', 'notification_frequency', 'notification_medium')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Verification', {'fields': ('email_verified',
                                     'phone_verified', 'verification_token')}),
        # For display purposes we use a computed property that shows the user's locations.
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # On creation, let admins assign locations via the many-to-many field.
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'user_locations', 'verbosity', 'notification_frequency', 'notification_medium')
        }),
    )

    def location_names(self, obj):
        # Use the many-to-many field 'user_locations'
        return ', '.join([loc.name for loc in obj.user_locations.all()])
    location_names.short_description = 'Location(s)'

    def location_coordinates(self, obj):
        return ', '.join([loc.coordinates for loc in obj.user_locations.all()])
    location_coordinates.short_description = 'Coordinates'

# Location Admin


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'coordinates', 'user_names')
    search_fields = ('name', 'coordinates')
    ordering = ('name',)
    # Update the fieldsets to remove the removed FK field.
    fieldsets = (
        (None, {'fields': ('name', 'coordinates')}),
    )

    def user_names(self, obj):
        # With only the ManyToManyField, use the reverse accessor 'users'
        # 'users' is the related_name from CustomUser.user_locations
        associated_users = obj.users.all()
        if associated_users.exists():
            return ', '.join([user.username for user in associated_users])
        return "No user"
    user_names.admin_order_field = 'user__username'
    user_names.short_description = 'User(s)'


# Register your models with the admin site.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Location, LocationAdmin)
