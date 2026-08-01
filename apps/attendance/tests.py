import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.departments.models import Department, Course
from apps.subjects.models import Semester, Section, Subject
from apps.faculty.models import Faculty
from apps.students.models import Student
from apps.attendance.models import QRSession, AttendanceRecord
from utils.security import generate_secure_token

User = get_user_model()

class QRValidationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(code='BTECH', name='B.Tech', department=self.dept)
        self.sem = Semester.objects.create(number=1, name='Sem 1')
        self.sec = Section.objects.create(name='Sec A')
        self.subject = Subject.objects.create(code='CS101', name='Intro to CS', department=self.dept, course=self.course, semester=self.sem)

        self.fac_user = User.objects.create_user(username='prof1', password='pass', role=User.Role.FACULTY)
        self.faculty = Faculty.objects.create(user=self.fac_user, employee_id='F1', department=self.dept)

        self.st_user = User.objects.create_user(username='student1', password='pass', role=User.Role.STUDENT)
        self.student = Student.objects.create(
            user=self.st_user, roll_number='R1', enrollment_number='E1',
            department=self.dept, course=self.course, semester=self.sem, section=self.sec
        )

    def test_qr_validation_success(self):
        token = generate_secure_token()
        qr_session = QRSession.objects.create(
            faculty=self.faculty, subject=self.subject, department=self.dept,
            semester=self.sem, section=self.sec, token=token,
            duration_minutes=5, expires_at=timezone.now() + timedelta(minutes=5), is_active=True
        )

        self.client.login(username='student1', password='pass')
        response = self.client.post('/students/api/validate-qr/', json.dumps({
            'qr_data': token,
            'device_info': 'Test Runner'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200, msg=f"Response json: {response.json()}")
        self.assertEqual(response.json()['status'], 'success')
        self.assertTrue(AttendanceRecord.objects.filter(student=self.student, subject=self.subject).exists())

    def test_expired_qr_validation(self):
        token = generate_secure_token()
        qr_session = QRSession.objects.create(
            faculty=self.faculty, subject=self.subject, department=self.dept,
            semester=self.sem, section=self.sec, token=token,
            duration_minutes=5, expires_at=timezone.now() - timedelta(minutes=5), is_active=True
        )

        self.client.login(username='student1', password='pass')
        response = self.client.post('/students/api/validate-qr/', json.dumps({
            'qr_data': token
        }), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['code'], 'QR_EXPIRED')
