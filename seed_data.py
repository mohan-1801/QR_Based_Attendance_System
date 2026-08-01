import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_qr_attendance.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from apps.departments.models import Department, Course, Branch
from apps.subjects.models import AcademicYear, Semester, Section, Classroom, Subject
from apps.faculty.models import Faculty
from apps.students.models import Student
from apps.attendance.models import QRSession, AttendanceRecord, AttendanceLog
from apps.notifications.models import Notification
from utils.security import generate_secure_token, encrypt_qr_payload

User = get_user_model()

def seed_database():
    print("Starting database seeding...")

    # 1. Super Admin Account
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@smartqr.com',
            'first_name': 'Super',
            'last_name': 'Admin',
            'role': User.Role.ADMIN,
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("Created Super Admin: admin / admin123")

    # 2. Academic Structure
    ay, _ = AcademicYear.objects.get_or_create(name='2025-2026', defaults={'is_current': True})
    sem5, _ = Semester.objects.get_or_create(number=5, defaults={'name': 'Semester 5', 'academic_year': ay})
    sec_a, _ = Section.objects.get_or_create(name='Section A', defaults={'capacity': 60})
    sec_b, _ = Section.objects.get_or_create(name='Section B', defaults={'capacity': 60})
    classroom, _ = Classroom.objects.get_or_create(room_number='LH-101', defaults={'building_name': 'Tech Block A', 'capacity': 60})

    # 3. Department & Course
    dept_cs, _ = Department.objects.get_or_create(
        code='CSE',
        defaults={'name': 'Computer Science & Engineering', 'description': 'Department of Computer Science', 'established_year': 2010}
    )
    course_btech, _ = Course.objects.get_or_create(
        code='BTECH-CS',
        defaults={'department': dept_cs, 'name': 'B.Tech Computer Science', 'degree_type': 'UG', 'duration_years': 4}
    )

    # 4. Subjects
    sub_dbms, _ = Subject.objects.get_or_create(
        code='CS501',
        defaults={'name': 'Database Management Systems', 'subject_type': 'THEORY', 'credits': 4, 'department': dept_cs, 'course': course_btech, 'semester': sem5}
    )
    sub_cn, _ = Subject.objects.get_or_create(
        code='CS502',
        defaults={'name': 'Computer Networks', 'subject_type': 'THEORY', 'credits': 4, 'department': dept_cs, 'course': course_btech, 'semester': sem5}
    )
    sub_lab, _ = Subject.objects.get_or_create(
        code='CS503',
        defaults={'name': 'DBMS Laboratory', 'subject_type': 'LAB', 'credits': 2, 'department': dept_cs, 'course': course_btech, 'semester': sem5}
    )

    # 5. Faculty Account
    fac_user, f_created = User.objects.get_or_create(
        username='faculty',
        defaults={
            'email': 'faculty@smartqr.com',
            'first_name': 'Dr. Alan',
            'last_name': 'Turing',
            'role': User.Role.FACULTY
        }
    )
    if f_created:
        fac_user.set_password('faculty123')
        fac_user.save()

    faculty_profile, _ = Faculty.objects.get_or_create(
        user=fac_user,
        defaults={'employee_id': 'FAC001', 'department': dept_cs, 'designation': 'Associate Professor'}
    )
    faculty_profile.assigned_subjects.add(sub_dbms, sub_cn, sub_lab)
    faculty_profile.assigned_sections.add(sec_a, sec_b)
    print("Created Faculty: faculty / faculty123")

    # 6. Student Accounts
    student_data = [
        ('student', '2024CS001', 'EN2024001', 'Alice', 'Smith', 'student@smartqr.com'),
        ('student2', '2024CS002', 'EN2024002', 'Bob', 'Jones', 'bob@smartqr.com'),
        ('student3', '2024CS003', 'EN2024003', 'Charlie', 'Brown', 'charlie@smartqr.com'),
        ('student4', '2024CS004', 'EN2024004', 'Diana', 'Prince', 'diana@smartqr.com'),
    ]

    students = []
    for uname, roll, enroll, fname, lname, email in student_data:
        st_user, created = User.objects.get_or_create(
            username=uname,
            defaults={'email': email, 'first_name': fname, 'last_name': lname, 'role': User.Role.STUDENT}
        )
        if created:
            st_user.set_password('student123')
            st_user.save()

        st_profile, _ = Student.objects.get_or_create(
            user=st_user,
            defaults={
                'roll_number': roll,
                'enrollment_number': enroll,
                'department': dept_cs,
                'course': course_btech,
                'semester': sem5,
                'section': sec_a
            }
        )
        students.append(st_profile)
    print("Created 4 Student accounts (Default login: student / student123)")

    # 7. Sample Attendance Records for past days
    today = timezone.now().date()
    for days_back in range(1, 6):
        past_date = today - timedelta(days=days_back)
        for st in students:
            status_choice = random.choice(['PRESENT', 'PRESENT', 'PRESENT', 'LATE', 'ABSENT'])
            AttendanceRecord.objects.get_or_create(
                student=st,
                subject=sub_dbms,
                date=past_date,
                defaults={'status': status_choice, 'verification_method': 'QR_SCAN'}
            )

    # 8. Active QR Session for Faculty
    token = generate_secure_token()
    now = timezone.now()
    expires_at = now + timedelta(minutes=15)
    payload = {'token': token, 'subject_id': sub_dbms.id, 'section_id': sec_a.id}
    encrypted = encrypt_qr_payload(payload)

    qr_session, _ = QRSession.objects.get_or_create(
        faculty=faculty_profile,
        subject=sub_dbms,
        department=dept_cs,
        semester=sem5,
        section=sec_a,
        token=token,
        defaults={
            'encrypted_payload': encrypted,
            'duration_minutes': 15,
            'expires_at': expires_at,
            'is_active': True
        }
    )

    # 9. Initial Notifications
    Notification.objects.get_or_create(
        user=admin_user,
        title="System Initialized",
        defaults={'message': "Smart QR Attendance System initialized with sample academic structure."}
    )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
