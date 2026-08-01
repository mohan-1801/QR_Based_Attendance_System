from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta, datetime

from apps.attendance.models import AttendanceRecord, QRSession
from apps.departments.models import Department, Course
from apps.subjects.models import Subject, Semester, Section
from apps.students.models import Student
from apps.faculty.models import Faculty
from utils.pdf_generator import generate_attendance_pdf
from utils.excel_generator import generate_attendance_excel

@login_required
def reports_index(request):
    departments = Department.objects.all()
    courses = Course.objects.all()
    semesters = Semester.objects.all()
    subjects = Subject.objects.all()

    # Filters from GET
    dept_id = request.GET.get('department')
    course_id = request.GET.get('course')
    sem_id = request.GET.get('semester')
    subj_id = request.GET.get('subject')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('report_type', 'daily')

    records = AttendanceRecord.objects.select_related('student__user', 'subject', 'student__department').all()

    if dept_id:
        records = records.filter(student__department_id=dept_id)
    if course_id:
        records = records.filter(student__course_id=course_id)
    if sem_id:
        records = records.filter(student__semester_id=sem_id)
    if subj_id:
        records = records.filter(subject_id=subj_id)
    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)

    total_records = records.count()
    present_count = records.filter(status='PRESENT').count()
    late_count = records.filter(status='LATE').count()
    absent_count = records.filter(status='ABSENT').count()

    overall_pct = round(((present_count + late_count) / max(total_records, 1)) * 100, 1)

    return render(request, 'reports/reports_index.html', {
        'departments': departments,
        'courses': courses,
        'semesters': semesters,
        'subjects': subjects,
        'records': records[:100],  # paginated view
        'total_records': total_records,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'overall_pct': overall_pct,
        'filters': request.GET
    })

@login_required
def chart_analytics_api(request):
    """
    JSON endpoint supplying formatted data for Chart.js charts:
    - Status Breakdown (Pie Chart)
    - Weekly Attendance Trend (Line Chart)
    - Department Breakdown (Bar Chart)
    """
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    # 1. Pie Chart
    records = AttendanceRecord.objects.all()
    present_cnt = records.filter(status='PRESENT').count()
    late_cnt = records.filter(status='LATE').count()
    absent_cnt = records.filter(status='ABSENT').count()

    # 2. Line Graph (Last 7 Days)
    dates_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        dates_labels.append(d.strftime('%b %d'))
        cnt = AttendanceRecord.objects.filter(date=d, status__in=['PRESENT', 'LATE']).count()
        trend_data.append(cnt)

    # 3. Bar Chart (Department breakdown)
    dept_labels = []
    dept_counts = []
    for dept in Department.objects.all():
        dept_labels.append(dept.code)
        cnt = AttendanceRecord.objects.filter(student__department=dept, status__in=['PRESENT', 'LATE']).count()
        dept_counts.append(cnt)

    return JsonResponse({
        'pie': {
            'labels': ['Present', 'Late', 'Absent'],
            'data': [present_cnt, late_cnt, absent_cnt]
        },
        'line': {
            'labels': dates_labels,
            'data': trend_data
        },
        'bar': {
            'labels': dept_labels,
            'data': dept_counts
        }
    })

@login_required
def export_filtered_pdf(request):
    records = AttendanceRecord.objects.select_related('student__user', 'subject').all()
    subj_id = request.GET.get('subject')
    if subj_id:
        records = records.filter(subject_id=subj_id)

    title = "Attendance Analytics & Summary Report"
    subtitle = f"Generated on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    metadata = {
        "Total Filtered Records": records.count(),
        "Exported By": request.user.get_full_name_or_username()
    }
    pdf_bytes = generate_attendance_pdf(title, subtitle, records, metadata)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
    return response

@login_required
def export_filtered_excel(request):
    records = AttendanceRecord.objects.select_related('student__user', 'subject').all()
    subj_id = request.GET.get('subject')
    if subj_id:
        records = records.filter(subject_id=subj_id)

    title = "Attendance Analytics Report"
    metadata = {
        "Total Records": records.count(),
        "Exported By": request.user.get_full_name_or_username()
    }
    excel_bytes = generate_attendance_excel(title, records, metadata)
    response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.xlsx"'
    return response
