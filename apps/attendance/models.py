import uuid
from django.db import models
from django.utils import timezone
from apps.faculty.models import Faculty
from apps.students.models import Student
from apps.departments.models import Department
from apps.subjects.models import Subject, Semester, Section

class QRSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='qr_sessions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='qr_sessions')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='qr_sessions')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='qr_sessions')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='qr_sessions')
    time_slot = models.CharField(max_length=100, default='09:00 AM - 10:00 AM')
    token = models.CharField(max_length=255, unique=True)
    encrypted_payload = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    geofence_radius_meters = models.IntegerField(default=100)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        if not self.is_active:
            return True
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"QR Session - {self.subject.code} ({self.section.name}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        LATE = 'LATE', 'Late'
        ABSENT = 'ABSENT', 'Absent'

    class VerificationMethod(models.TextChoices):
        QR_SCAN = 'QR_SCAN', 'QR Scan'
        MANUAL = 'MANUAL', 'Manual Correction'
        GPS_VERIFIED = 'GPS_VERIFIED', 'GPS Verified QR'
        FACE_VERIFIED = 'FACE_VERIFIED', 'Face Verification'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    session = models.ForeignKey(QRSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='records')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    marked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    verification_method = models.CharField(max_length=30, choices=VerificationMethod.choices, default=VerificationMethod.QR_SCAN)
    scanned_latitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    scanned_longitude = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-marked_at']
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code} - {self.date} ({self.status})"

class AttendanceLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    session = models.ForeignKey(QRSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    action = models.CharField(max_length=150)
    status = models.CharField(max_length=30, default='SUCCESS')
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.status}] {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
