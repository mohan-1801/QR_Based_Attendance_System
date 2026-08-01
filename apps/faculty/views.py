from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import json

from .models import Faculty
from apps.departments.models import Department
from apps.subjects.models import Subject, Semester, Section
from apps.attendance.models import QRSession, AttendanceRecord, AttendanceLog
from utils.security import generate_secure_token, encrypt_qr_payload
from utils.qr_generator import generate_qr_code_image
from utils.pdf_generator import generate_attendance_pdf
from utils.excel_generator import generate_attendance_excel

User = get_user_model()

def faculty_or_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or (not request.user.is_faculty() and not request.user.is_admin()):
            messages.error(request, "Access restricted to faculty members and administrators.")
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def faculty_list(request):
    if not request.user.is_admin():
        messages.error(request, "Only Super Admin can manage faculty profiles.")
        return redirect('dashboard:dashboard')

    faculties = Faculty.objects.select_related('user', 'department').all()
    departments = Department.objects.all()
    subjects = Subject.objects.all()
    sections = Section.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_faculty':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password', 'faculty123')
            employee_id = request.POST.get('employee_id')
            dept_id = request.POST.get('department')
            designation = request.POST.get('designation', 'Assistant Professor')

            if username and employee_id and email:
                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Username '{username}' is already taken.")
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=User.Role.FACULTY
                    )
                    dept = Department.objects.get(id=dept_id) if dept_id else None
                    faculty = Faculty.objects.create(
                        user=user,
                        employee_id=employee_id,
                        department=dept,
                        designation=designation
                    )
                    messages.success(request, f"Faculty {user.get_full_name_or_username()} created successfully.")
                    return redirect('faculty:faculty_list')

        elif action == 'assign_subjects':
            faculty_id = request.POST.get('faculty_id')
            assigned_sub_ids = request.POST.getlist('subjects')
            assigned_sec_ids = request.POST.getlist('sections')
            faculty = get_object_or_404(Faculty, pk=faculty_id)
            faculty.assigned_subjects.set(assigned_sub_ids)
            faculty.assigned_sections.set(assigned_sec_ids)
            messages.success(request, f"Assigned subjects and sections updated for {faculty.user.get_full_name_or_username()}.")
            return redirect('faculty:faculty_list')

    return render(request, 'faculty/faculty_list.html', {
        'faculties': faculties,
        'departments': departments,
        'subjects': subjects,
        'sections': sections
    })

@login_required
def delete_faculty(request, pk):
    if not request.user.is_admin():
        messages.error(request, "Permission denied.")
        return redirect('dashboard:dashboard')
    faculty = get_object_or_404(Faculty, pk=pk)
    user = faculty.user
    faculty.delete()
    user.delete()
    messages.success(request, "Faculty account removed successfully.")
    return redirect('faculty:faculty_list')

@login_required
@faculty_or_admin_required
def generate_qr_view(request):
    try:
        faculty = request.user.faculty_profile
    except Exception:
        # Fallback if admin is viewing
        faculty = Faculty.objects.first()

    subjects = faculty.assigned_subjects.all() if faculty and faculty.assigned_subjects.exists() else Subject.objects.all()
    sections = Section.objects.all()
    departments = Department.objects.all()
    semesters = Semester.objects.all()

    active_session = None
    if faculty:
        active_session = QRSession.objects.filter(faculty=faculty, is_active=True, expires_at__gt=timezone.now()).first()

    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        dept_id = request.POST.get('department')
        sem_id = request.POST.get('semester')
        sec_id = request.POST.get('section')
        time_slot = request.POST.get('time_slot', '09:00 AM - 10:00 AM')
        duration_mins = int(request.POST.get('duration_minutes', 3))
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None

        if subject_id and dept_id and sem_id and sec_id:
            subject = get_object_or_404(Subject, pk=subject_id)
            department = get_object_or_404(Department, pk=dept_id)
            semester = get_object_or_404(Semester, pk=sem_id)
            section = get_object_or_404(Section, pk=sec_id)

            # Deactivate previous active sessions for this faculty
            if faculty:
                QRSession.objects.filter(faculty=faculty, is_active=True).update(is_active=False)

            token = generate_secure_token()
            now = timezone.now()
            expires_at = now + timedelta(minutes=duration_mins)

            payload = {
                'token': token,
                'faculty_id': faculty.id if faculty else 1,
                'subject_id': subject.id,
                'section_id': section.id,
                'timestamp': now.timestamp(),
                'expires_at': expires_at.timestamp(),
            }

            encrypted_payload = encrypt_qr_payload(payload)

            qr_session = QRSession.objects.create(
                faculty=faculty,
                subject=subject,
                department=department,
                semester=semester,
                section=section,
                time_slot=time_slot,
                token=token,
                encrypted_payload=encrypted_payload,
                duration_minutes=duration_mins,
                expires_at=expires_at,
                is_active=True,
                latitude=latitude,
                longitude=longitude
            )

            file_name, content_file = generate_qr_code_image(token, qr_session.session_id)
            qr_session.qr_image.save(file_name, content_file, save=True)

            messages.success(request, f"Live QR Code generated for {subject.name} ({section.name}). Valid for {duration_mins} minutes.")
            return redirect('faculty:live_session', session_id=qr_session.session_id)

    return render(request, 'faculty/generate_qr.html', {
        'subjects': subjects,
        'sections': sections,
        'departments': departments,
        'semesters': semesters,
        'active_session': active_session
    })

@login_required
@faculty_or_admin_required
def live_session_view(request, session_id):
    qr_session = get_object_or_404(QRSession, session_id=session_id)
    records = AttendanceRecord.objects.filter(session=qr_session).select_related('student__user')
    return render(request, 'faculty/live_session.html', {
        'qr_session': qr_session,
        'records': records
    })

@login_required
@faculty_or_admin_required
def stop_session_view(request, session_id):
    qr_session = get_object_or_404(QRSession, session_id=session_id)
    qr_session.is_active = False
    qr_session.save()
    messages.info(request, "QR Attendance session ended.")
    return redirect('faculty:live_session', session_id=session_id)

@login_required
@faculty_or_admin_required
def live_session_data_api(request, session_id):
    qr_session = get_object_or_404(QRSession, session_id=session_id)
    records = AttendanceRecord.objects.filter(session=qr_session).select_related('student__user')

    is_expired = qr_session.is_expired()

    data = {
        'is_active': qr_session.is_active and not is_expired,
        'is_expired': is_expired,
        'expires_at_iso': qr_session.expires_at.isoformat(),
        'total_count': records.count(),
        'present_count': records.filter(status='PRESENT').count(),
        'late_count': records.filter(status='LATE').count(),
        'records': [
            {
                'id': r.id,
                'roll_number': r.student.roll_number,
                'name': r.student.user.get_full_name_or_username(),
                'marked_at': r.marked_at.strftime('%H:%M:%S'),
                'status': r.status,
                'method': r.get_verification_method_display()
            } for r in records
        ]
    }
    return JsonResponse(data)

@login_required
@faculty_or_admin_required
def manual_attendance_view(request):
    subjects = Subject.objects.all()
    sections = Section.objects.all()

    records = []
    selected_subject = None
    selected_section = None
    selected_date = timezone.now().date()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'search':
            sub_id = request.POST.get('subject')
            sec_id = request.POST.get('section')
            date_str = request.POST.get('date')
            if sub_id and sec_id:
                selected_subject = Subject.objects.get(id=sub_id)
                selected_section = Section.objects.get(id=sec_id)
                if date_str:
                    selected_date = date_str
                records = AttendanceRecord.objects.filter(
                    subject=selected_subject,
                    student__section=selected_section,
                    date=selected_date
                ).select_related('student__user')

        elif action == 'save_manual':
            sub_id = request.POST.get('subject_id')
            sec_id = request.POST.get('section_id')
            date_val = request.POST.get('date_val')
            
            student_ids = request.POST.getlist('student_ids')
            for st_id in student_ids:
                status = request.POST.get(f'status_{st_id}')
                if status:
                    from apps.students.models import Student
                    student = Student.objects.get(id=st_id)
                    subject = Subject.objects.get(id=sub_id)
                    AttendanceRecord.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=date_val,
                        defaults={
                            'status': status,
                            'verification_method': AttendanceRecord.VerificationMethod.MANUAL
                        }
                    )
            messages.success(request, "Manual attendance records saved successfully.")
            return redirect('faculty:manual_attendance')

    return render(request, 'faculty/manual_attendance.html', {
        'subjects': subjects,
        'sections': sections,
        'records': records,
        'selected_subject': selected_subject,
        'selected_section': selected_section,
        'selected_date': selected_date
    })

@login_required
@faculty_or_admin_required
def export_session_pdf(request, session_id):
    qr_session = get_object_or_404(QRSession, session_id=session_id)
    records = AttendanceRecord.objects.filter(session=qr_session).select_related('student__user', 'subject')

    title = f"Attendance Sheet - {qr_session.subject.name}"
    subtitle = f"Department: {qr_session.department.name} | Section: {qr_session.section.name} | Date: {qr_session.created_at.strftime('%Y-%m-%d')}"
    metadata = {
        "Faculty": qr_session.faculty.user.get_full_name_or_username(),
        "Subject Code": qr_session.subject.code,
        "Time Slot": qr_session.time_slot,
        "Total Present": records.count()
    }

    pdf_bytes = generate_attendance_pdf(title, subtitle, records, metadata)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{qr_session.session_id}.pdf"'
    return response

@login_required
@faculty_or_admin_required
def export_session_excel(request, session_id):
    qr_session = get_object_or_404(QRSession, session_id=session_id)
    records = AttendanceRecord.objects.filter(session=qr_session).select_related('student__user', 'subject')

    title = f"Attendance Sheet - {qr_session.subject.name} ({qr_session.section.name})"
    metadata = {
        "Faculty": qr_session.faculty.user.get_full_name_or_username(),
        "Department": qr_session.department.name,
        "Date": qr_session.created_at.strftime('%Y-%m-%d'),
        "Time Slot": qr_session.time_slot
    }

    excel_bytes = generate_attendance_excel(title, records, metadata)
    response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="attendance_{qr_session.session_id}.xlsx"'
    return response
