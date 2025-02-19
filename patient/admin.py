from django.contrib import admin

from .models import Patient, OTP
from django.contrib.auth.models import User

class DonorAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'get_user_name', 'get_location', 'location_name', 'is_email_verified', 'mobile')  # Added location_name
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'address', 'mobile')  # Enable search by these fields
    list_filter = ('user__is_active',)  # Filter by email verification status
    readonly_fields = ('get_map', 'location_name')  # Added location_name as read-only
    fieldsets = (
        ('Personal Info', {
            'fields': ('get_user_name', 'get_user_email', 'address', 'mobile', 'profile_pic'),
        }),
        ('Location Info', {
            'fields': ('latitude', 'longitude', 'get_map', 'location_name'),  # Added location_name
        }),
        ('Verification', {
            'fields': ('is_email_verified',),
        }),
    )

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

    def get_user_name(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name
    get_user_name.short_description = 'Name'

    def get_location(self, obj):
        return f"Lat: {obj.latitude}, Lon: {obj.longitude}"
    get_location.short_description = 'Location'

    def is_email_verified(self, obj):
        return obj.user.is_active
    is_email_verified.boolean = True  # Display as a boolean field
    is_email_verified.short_description = 'Email Verified'

    def get_map(self, obj):
        if obj.latitude and obj.longitude:
            return (
                f'<iframe width="100%" height="400" '
                f'src="https://maps.google.com/maps?q={obj.latitude},{obj.longitude}&hl=es&z=14&amp;output=embed"></iframe>'
            )
        return "No location available"
    get_map.short_description = 'Location Map'
    get_map.allow_tags = True  # Enable HTML rendering in the admin panel


class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'created_at')
    search_fields = ('user__email', 'user__username', 'otp_code')
    list_filter = ('created_at',)





admin.site.register(Patient, DonorAdmin)
admin.site.register(OTP, OTPAdmin)

