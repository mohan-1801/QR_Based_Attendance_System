from django.db import models
from django.conf import settings
from apps.departments.models import Department, Course, Branch
from apps.subjects.models import Semester, Section

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
    enrollment_number = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    batch_year = models.IntegerField(default=2024)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['roll_number']

    def get_attendance_percentage(self, subject=None):
        from apps.attendance.models import AttendanceRecord
        records = AttendanceRecord.objects.filter(student=self)
        if subject:
            records = records.filter(subject=subject)
        total = records.count()
        if total == 0:
            return 100.0
        present = records.filter(status__in=['PRESENT', 'LATE']).count()
        return round((present / total) * 100, 1)

    def __str__(self):
        return f"{self.user.get_full_name_or_username()} ({self.roll_number})"
