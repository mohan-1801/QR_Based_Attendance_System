from django.contrib import admin
from .models import AcademicYear, Semester, Section, Classroom, Subject

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_current', 'created_at')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'academic_year')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'building_name', 'capacity')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'subject_type', 'credits', 'department', 'semester')
    list_filter = ('department', 'subject_type', 'semester')
    search_fields = ('code', 'name')
