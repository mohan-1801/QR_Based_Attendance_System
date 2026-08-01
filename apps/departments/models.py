from django.db import models

class Department(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    established_year = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class Course(models.Model):
    class DegreeType(models.TextChoices):
        UNDERGRADUATE = 'UG', 'Undergraduate'
        POSTGRADUATE = 'PG', 'Postgraduate'
        DIPLOMA = 'DIPLOMA', 'Diploma'
        PHD = 'PHD', 'Doctorate'

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    degree_type = models.CharField(max_length=20, choices=DegreeType.choices, default=DegreeType.UNDERGRADUATE)
    duration_years = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.department.code}"

class Branch(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='branches')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.course.code})"
