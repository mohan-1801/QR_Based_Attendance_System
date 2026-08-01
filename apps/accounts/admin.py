from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_approved', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Additional Info', {'fields': ('role', 'phone_number', 'profile_picture', 'address', 'date_of_birth', 'is_approved')}),
    )
