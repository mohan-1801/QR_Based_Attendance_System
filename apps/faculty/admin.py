from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'designation', 'joining_date')
    list_filter = ('department', 'designation')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name')
