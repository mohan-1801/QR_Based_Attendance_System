from django.db import models
from django.conf import settings
from apps.departments.models import Department
from apps.subjects.models import Subject, Section

class Faculty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='faculty_members')
    designation = models.CharField(max_length=100, default='Assistant Professor')
    qualification = models.CharField(max_length=150, blank=True, null=True)
    joining_date = models.DateField(blank=True, null=True)
    assigned_subjects = models.ManyToManyField(Subject, blank=True, related_name='assigned_faculty')
    assigned_sections = models.ManyToManyField(Section, blank=True, related_name='assigned_faculty')

    class Meta:
        verbose_name_plural = "Faculty Members"
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.user.get_full_name_or_username()} ({self.employee_id})"
