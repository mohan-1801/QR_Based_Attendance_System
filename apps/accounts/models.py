from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Super Admin'
        FACULTY = 'FACULTY', 'Faculty'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_approved = models.BooleanField(default=True)

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_faculty(self):
        return self.role == self.Role.FACULTY

    def is_student(self):
        return self.role == self.Role.STUDENT

    def get_full_name_or_username(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
