from django.contrib import admin
from .models import Department, Course, Branch

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'established_year', 'created_at')
    search_fields = ('code', 'name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'degree_type', 'duration_years')
    list_filter = ('department', 'degree_type')
    search_fields = ('code', 'name')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course')
    search_fields = ('code', 'name')
