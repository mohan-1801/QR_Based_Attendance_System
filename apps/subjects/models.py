from django.db import models
from apps.departments.models import Department, Course

class AcademicYear(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g. 2025-2026")
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-name']

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Semester(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters', null=True, blank=True)
    number = models.IntegerField(help_text="1 to 8")
    name = models.CharField(max_length=50, help_text="e.g. Semester 1")

    class Meta:
        ordering = ['number']

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=50, help_text="e.g. Section A")
    capacity = models.IntegerField(default=60)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Classroom(models.Model):
    room_number = models.CharField(max_length=50, unique=True)
    building_name = models.CharField(max_length=100)
    capacity = models.IntegerField(default=60)

    class Meta:
        ordering = ['room_number']

    def __str__(self):
        return f"{self.room_number} ({self.building_name})"

class Subject(models.Model):
    class SubjectType(models.TextChoices):
        THEORY = 'THEORY', 'Theory'
        LAB = 'LAB', 'Practical / Lab'
        PROJECT = 'PROJECT', 'Project'

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    subject_type = models.CharField(max_length=20, choices=SubjectType.choices, default=SubjectType.THEORY)
    credits = models.IntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='subjects')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"
