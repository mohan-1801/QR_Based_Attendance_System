from rest_framework import serializers
from apps.accounts.models import User
from apps.students.models import Student
from apps.faculty.models import Faculty
from apps.departments.models import Department, Course
from apps.subjects.models import Subject, Semester, Section
from apps.attendance.models import QRSession, AttendanceRecord

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Subject
        fields = '__all__'

class FacultySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    class Meta:
        model = Faculty
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    attendance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_attendance_percentage(self, obj):
        return obj.get_attendance_percentage()

class QRSessionSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.user.get_full_name_or_username', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = QRSession
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)
    student_name = serializers.CharField(source='student.user.get_full_name_or_username', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = '__all__'
