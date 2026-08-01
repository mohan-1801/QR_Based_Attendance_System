from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'enrollment_number', 'user', 'department', 'course', 'section')
    list_filter = ('department', 'course', 'semester', 'section')
    search_fields = ('roll_number', 'enrollment_number', 'user__username', 'user__first_name', 'user__last_name')
