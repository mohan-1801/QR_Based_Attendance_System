from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime
import openpyxl
import json

from .models import Student
from apps.departments.models import Department, Course, Branch
from apps.subjects.models import Semester, Section, Subject
from apps.attendance.models import QRSession, AttendanceRecord, AttendanceLog
from utils.security import decrypt_qr_payload
from utils.excel_generator import generate_attendance_excel

User = get_user_model()

@login_required
def student_list(request):
    if not request.user.is_admin() and not request.user.is_faculty():
        messages.error(request, "Permission denied.")
        return redirect('dashboard:dashboard')

    students = Student.objects.select_related('user', 'department', 'course', 'semester', 'section').all()
    departments = Department.objects.all()
    courses = Course.objects.all()
    semesters = Semester.objects.all()
    sections = Section.objects.all()

    if request.method == 'POST' and request.user.is_admin():
        action = request.POST.get('action')
        if action == 'add_student':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password', 'student123')
            roll_number = request.POST.get('roll_number')
            enrollment_number = request.POST.get('enrollment_number')
            dept_id = request.POST.get('department')
            course_id = request.POST.get('course')
            sem_id = request.POST.get('semester')
            sec_id = request.POST.get('section')
            photo = request.FILES.get('photo')

            if username and roll_number and enrollment_number and email:
                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Username '{username}' already exists.")
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=User.Role.STUDENT
                    )
                    dept = Department.objects.get(id=dept_id) if dept_id else None
                    course = Course.objects.get(id=course_id) if course_id else None
                    sem = Semester.objects.get(id=sem_id) if sem_id else None
                    sec = Section.objects.get(id=sec_id) if sec_id else None

                    Student.objects.create(
                        user=user,
                        roll_number=roll_number,
                        enrollment_number=enrollment_number,
                        department=dept,
                        course=course,
                        semester=sem,
                        section=sec,
                        photo=photo
                    )
                    messages.success(request, f"Student {roll_number} - {first_name} added successfully.")
                    return redirect('students:student_list')

    return render(request, 'students/student_list.html', {
        'students': students,
        'departments': departments,
        'courses': courses,
        'semesters': semesters,
        'sections': sections
    })

@login_required
def delete_student(request, pk):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard:dashboard')
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, "Student account removed successfully.")
    return redirect('students:student_list')

@login_required
def import_students_excel(request):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard:dashboard')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']
        count = 0
        try:
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            for idx, row in enumerate(ws.iter_rows(values_only=True)):
                if idx == 0:  # Header
                    continue
                if not row or not row[0]:
                    continue

                username = str(row[0]).strip()
                first_name = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                last_name = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                email = str(row[3]).strip() if len(row) > 3 and row[3] else f"{username}@student.com"
                roll_no = str(row[4]).strip() if len(row) > 4 and row[4] else username
                enroll_no = str(row[5]).strip() if len(row) > 5 and row[5] else f"EN_{roll_no}"

                if not User.objects.filter(username=username).exists() and not Student.objects.filter(roll_number=roll_no).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password='student123',
                        first_name=first_name,
                        last_name=last_name,
                        role=User.Role.STUDENT
                    )
                    dept = Department.objects.first()
                    course = Course.objects.first()
                    sem = Semester.objects.first()
                    sec = Section.objects.first()
                    Student.objects.create(
                        user=user,
                        roll_number=roll_no,
                        enrollment_number=enroll_no,
                        department=dept,
                        course=course,
                        semester=sem,
                        section=sec
                    )
                    count += 1
            messages.success(request, f"Successfully imported {count} students!")
        except Exception as e:
            messages.error(request, f"Error reading Excel file: {str(e)}")
        return redirect('students:student_list')

    return render(request, 'students/import_students.html')

@login_required
def export_students_excel(request):
    if not request.user.is_admin() and not request.user.is_faculty():
        messages.error(request, "Permission denied.")
        return redirect('dashboard:dashboard')

    students = Student.objects.select_related('user', 'department', 'course', 'section').all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Directory"

    headers = ["Roll Number", "Enrollment No", "Full Name", "Email", "Department", "Course", "Section"]
    ws.append(headers)

    for st in students:
        ws.append([
            st.roll_number,
            st.enrollment_number,
            st.user.get_full_name_or_username(),
            st.user.email,
            st.department.name if st.department else "N/A",
            st.course.name if st.course else "N/A",
            st.section.name if st.section else "N/A",
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students_list.xlsx"'
    wb.save(response)
    return response

@login_required
def scan_qr_page(request):
    if not request.user.is_student():
        messages.warning(request, "Faculty/Admins can test QR scanning here, but attendance requires a student account.")
    return render(request, 'students/scan_qr.html')

@login_required
def validate_qr_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP Method'}, status=405)

    data = {}
    if request.body:
        try:
            body_str = request.body.decode('utf-8')
            if body_str:
                data = json.loads(body_str)
        except Exception:
            pass

    if not data and request.POST:
        data = request.POST.dict()

    raw_qr_token = data.get('qr_data', '').strip()
    scanned_lat = data.get('latitude')
    scanned_long = data.get('longitude')
    device_info = data.get('device_info', 'Web Browser')

    if not raw_qr_token:
        return JsonResponse({'status': 'error', 'message': 'Empty QR token.'}, status=400)

    # 1. Student check
    try:
        student = request.user.student_profile
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'User profile is not registered as a Student.'}, status=403)

    # 2. Check token in QRSession table
    qr_session = QRSession.objects.filter(token=raw_qr_token).first()
    if not qr_session:
        payload = decrypt_qr_payload(raw_qr_token)
        if payload and 'token' in payload:
            qr_session = QRSession.objects.filter(token=payload['token']).first()

    if not qr_session:
        AttendanceLog.objects.create(
            student=student,
            action="QR Scan Attempt",
            status="FAILED",
            details="Invalid or unrecognized QR Code token."
        )
        return JsonResponse({'status': 'error', 'message': 'Invalid QR Code token.'}, status=400)

    # 3. Check expiration & active status
    if qr_session.is_expired():
        AttendanceLog.objects.create(
            student=student,
            session=qr_session,
            action="QR Scan Expired",
            status="FAILED",
            details=f"QR Session expired at {qr_session.expires_at}"
        )
        return JsonResponse({
            'status': 'error',
            'code': 'QR_EXPIRED',
            'message': 'QR Code has expired! Please ask faculty to regenerate.'
        }, status=400)

    # 4. Check Section & Subject match
    if student.section and qr_session.section and student.section != qr_session.section:
        AttendanceLog.objects.create(
            student=student,
            session=qr_session,
            action="Section Mismatch",
            status="FAILED",
            details=f"Student section {student.section.name} != Session section {qr_session.section.name}"
        )
        return JsonResponse({
            'status': 'error',
            'code': 'SECTION_MISMATCH',
            'message': f'This QR code is intended for {qr_session.section.name}. You belong to {student.section.name if student.section else "unassigned"}.'
        }, status=400)

    # 5. Check Duplicate Attendance
    today = timezone.now().date()
    existing_record = AttendanceRecord.objects.filter(
        student=student,
        subject=qr_session.subject,
        date=today
    ).first()

    if existing_record:
        AttendanceLog.objects.create(
            student=student,
            session=qr_session,
            action="Duplicate Scan Blocked",
            status="WARNING",
            details=f"Attendance already marked for subject {qr_session.subject.code} at {existing_record.marked_at}"
        )
        return JsonResponse({
            'status': 'warning',
            'code': 'ALREADY_MARKED',
            'message': f'Attendance already marked for {qr_session.subject.name} on {today}!'
        })

    # 6. Success -> Mark Attendance
    record = AttendanceRecord.objects.create(
        student=student,
        session=qr_session,
        subject=qr_session.subject,
        date=today,
        status=AttendanceRecord.Status.PRESENT,
        verification_method=AttendanceRecord.VerificationMethod.QR_SCAN,
        scanned_latitude=scanned_lat,
        scanned_longitude=scanned_long,
        device_info=device_info
    )

    AttendanceLog.objects.create(
        student=student,
        session=qr_session,
        action="Attendance Marked Successfully",
        status="SUCCESS",
        details=f"Subject: {qr_session.subject.code}, Time: {record.marked_at.strftime('%H:%M:%S')}"
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Attendance marked successfully!',
        'details': {
            'subject_name': qr_session.subject.name,
            'subject_code': qr_session.subject.code,
            'faculty_name': qr_session.faculty.user.get_full_name_or_username(),
            'marked_at': record.marked_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@login_required
def student_history_view(request):
    if request.user.is_student():
        student = request.user.student_profile
    else:
        student = Student.objects.first()

    records = AttendanceRecord.objects.filter(student=student).select_related('subject', 'session__faculty__user')
    attendance_pct = student.get_attendance_percentage() if student else 100.0

    return render(request, 'students/attendance_history.html', {
        'records': records,
        'student': student,
        'attendance_pct': attendance_pct
    })
