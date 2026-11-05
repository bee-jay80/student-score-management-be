from django.contrib import admin

from .models import User, EmailOTP

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('email',)

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_hash', 'purpose', 'created_at', 'is_used')
    search_fields = ('user__email', 'otp_hash', 'purpose')
    list_filter = ('purpose', 'is_used', 'created_at')
    ordering = ('-created_at',)