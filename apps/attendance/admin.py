from django.contrib import admin
from .models import QRSession, AttendanceRecord, AttendanceLog

@admin.register(QRSession)
class QRSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'faculty', 'subject', 'section', 'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'subject', 'section')
    search_fields = ('token', 'subject__name', 'faculty__user__username')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'marked_at', 'status', 'verification_method')
    list_filter = ('status', 'verification_method', 'subject', 'date')
    search_fields = ('student__roll_number', 'student__user__username', 'subject__code')

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'status', 'student', 'timestamp', 'ip_address')
    list_filter = ('status', 'timestamp')
    search_fields = ('action', 'details')
