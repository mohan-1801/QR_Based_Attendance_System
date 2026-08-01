from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from apps.students.models import Student
from apps.faculty.models import Faculty
from apps.attendance.models import QRSession, AttendanceRecord
from apps.subjects.models import Subject, Section, Semester
from apps.departments.models import Department
from .serializers import (
    StudentSerializer, FacultySerializer, QRSessionSerializer,
    AttendanceRecordSerializer, SubjectSerializer, DepartmentSerializer
)
from utils.security import generate_secure_token, encrypt_qr_payload
from utils.qr_generator import generate_qr_code_image

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'department', 'course', 'section').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.select_related('user', 'department').all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related('student__user', 'subject').all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_qr_api(request):
    """
    POST API to generate a new dynamic QR Code session.
    """
    user = request.user
    if not hasattr(user, 'faculty_profile') and not user.is_admin():
        return Response({'error': 'Only faculty or admins can generate QR sessions.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        faculty = user.faculty_profile if hasattr(user, 'faculty_profile') else Faculty.objects.first()
        subject_id = request.data.get('subject_id')
        section_id = request.data.get('section_id')
        dept_id = request.data.get('department_id')
        sem_id = request.data.get('semester_id')
        duration_minutes = int(request.data.get('duration_minutes', 5))

        subject = Subject.objects.get(id=subject_id)
        section = Section.objects.get(id=section_id)
        department = Department.objects.get(id=dept_id) if dept_id else subject.department
        semester = Semester.objects.get(id=sem_id) if sem_id else subject.semester

        token = generate_secure_token()
        now = timezone.now()
        expires_at = now + timedelta(minutes=duration_minutes)

        payload = {
            'token': token,
            'faculty_id': faculty.id,
            'subject_id': subject.id,
            'section_id': section.id,
            'timestamp': now.timestamp(),
            'expires_at': expires_at.timestamp()
        }
        encrypted = encrypt_qr_payload(payload)

        qr_session = QRSession.objects.create(
            faculty=faculty,
            subject=subject,
            department=department,
            semester=semester,
            section=section,
            token=token,
            encrypted_payload=encrypted,
            duration_minutes=duration_minutes,
            expires_at=expires_at,
            is_active=True
        )

        file_name, content_file = generate_qr_code_image(token, qr_session.session_id)
        qr_session.qr_image.save(file_name, content_file, save=True)

        serializer = QRSessionSerializer(qr_session, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
