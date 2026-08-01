from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from apps.accounts.models import User
from apps.faculty.models import Faculty
from apps.students.models import Student
from apps.departments.models import Department, Course
from apps.subjects.models import Subject, Section
from apps.attendance.models import AttendanceRecord, QRSession
from apps.notifications.models import Notification

@login_required
def dashboard_router(request):
    user = request.user
    if user.is_admin():
        return admin_dashboard(request)
    elif user.is_faculty():
        return faculty_dashboard(request)
    else:
        return student_dashboard(request)

@login_required
def admin_dashboard(request):
    total_faculty = Faculty.objects.count()
    total_students = Student.objects.count()
    total_departments = Department.objects.count()
    total_subjects = Subject.objects.count()

    today = timezone.now().date()
    today_records = AttendanceRecord.objects.filter(date=today)
    today_present = today_records.filter(status='PRESENT').count()
    today_late = today_records.filter(status='LATE').count()
    today_absent = today_records.filter(status='ABSENT').count()

    recent_sessions = QRSession.objects.select_related('faculty__user', 'subject', 'section')[:5]
    recent_logs = AttendanceRecord.objects.select_related('student__user', 'subject').order_by('-marked_at')[:8]

    # Attendance stats pie data
    total_marked = today_records.count() or 1
    pct_present = round((today_present / total_marked) * 100, 1)

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_faculty': total_faculty,
        'total_students': total_students,
        'total_departments': total_departments,
        'total_subjects': total_subjects,
        'today_present': today_present,
        'today_late': today_late,
        'today_absent': today_absent,
        'pct_present': pct_present,
        'recent_sessions': recent_sessions,
        'recent_logs': recent_logs,
    })

@login_required
def faculty_dashboard(request):
    try:
        faculty = request.user.faculty_profile
    except Exception:
        faculty = None

    assigned_subjects = faculty.assigned_subjects.all() if faculty else Subject.objects.none()
    assigned_sections = faculty.assigned_sections.all() if faculty else Section.objects.none()

    today = timezone.now().date()
    active_qr = QRSession.objects.filter(faculty=faculty, is_active=True, expires_at__gt=timezone.now()).first() if faculty else None

    my_sessions = QRSession.objects.filter(faculty=faculty).select_related('subject', 'section')[:6] if faculty else []

    return render(request, 'dashboard/faculty_dashboard.html', {
        'faculty': faculty,
        'assigned_subjects': assigned_subjects,
        'assigned_sections': assigned_sections,
        'active_qr': active_qr,
        'my_sessions': my_sessions,
    })

@login_required
def student_dashboard(request):
    try:
        student = request.user.student_profile
    except Exception:
        student = None

    records = AttendanceRecord.objects.filter(student=student).select_related('subject', 'session__faculty__user') if student else []
    total_classes = records.count()
    present_classes = records.filter(status__in=['PRESENT', 'LATE']).count()
    attendance_pct = student.get_attendance_percentage() if student else 100.0

    low_attendance_warning = attendance_pct < 75.0 and total_classes > 0

    return render(request, 'dashboard/student_dashboard.html', {
        'student': student,
        'total_classes': total_classes,
        'present_classes': present_classes,
        'attendance_pct': attendance_pct,
        'low_attendance_warning': low_attendance_warning,
        'recent_records': records[:7]
    })
