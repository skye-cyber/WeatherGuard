from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomRegistrationForm
from .models import CustomUser, Location

# Custom User Admin


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone',
                    'location_names', 'location_coordinates', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Verification', {'fields': ('email_verified', 'phone_verified', 'verification_token')}),
        ('Locations', {'fields': ('locations',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'locations')}
         ),
    )

    def location_names(self, obj):
        return ', '.join([loc.name for loc in obj.locations.all()])
    location_names.short_description = 'Location Names'

    def location_coordinates(self, obj):
        return ', '.join([loc.coordinates for loc in obj.locations.all()])
    location_coordinates.short_description = 'Location Coordinates'

# Location Admin


class LocationAdmin(admin.ModelAdmin):
    form = CustomRegistrationForm
    list_display = ('name', 'coordinates', 'user_names')
    list_filter = ('user__username',)  # Filter by user's username
    search_fields = ('name', 'coordinates', 'user__username')
    ordering = ('name',)
    fieldsets = (
        (None, {'fields': ('user', 'name', 'coordinates')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'name', 'coordinates')}
         ),
    )

    def user_names(self, obj):
        return ', '.join([user.username for user in obj.users.all()])
    user_names.admin_order_field = 'user__username'  # Allows column order sorting
    user_names.short_description = 'Users'  # Renames column head


# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Location, LocationAdmin)
