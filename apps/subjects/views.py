from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AcademicYear, Semester, Section, Classroom, Subject
from apps.departments.models import Department, Course

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            messages.error(request, "Access restricted to administrators.")
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@admin_required
def subject_list(request):
    subjects = Subject.objects.select_related('department', 'course', 'semester').all()
    departments = Department.objects.all()
    courses = Course.objects.all()
    semesters = Semester.objects.all()

    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        subject_type = request.POST.get('subject_type')
        credits = request.POST.get('credits', 3)
        dept_id = request.POST.get('department')
        course_id = request.POST.get('course')
        sem_id = request.POST.get('semester')

        if code and name and dept_id and course_id and sem_id:
            dept = get_object_or_404(Department, pk=dept_id)
            course = get_object_or_404(Course, pk=course_id)
            sem = get_object_or_404(Semester, pk=sem_id)
            Subject.objects.create(
                code=code, name=name, subject_type=subject_type, credits=credits,
                department=dept, course=course, semester=sem
            )
            messages.success(request, f"Subject '{name}' created successfully.")
            return redirect('subjects:subject_list')

    return render(request, 'subjects/subject_list.html', {
        'subjects': subjects,
        'departments': departments,
        'courses': courses,
        'semesters': semesters
    })

@login_required
@admin_required
def delete_subject(request, pk):
    subj = get_object_or_404(Subject, pk=pk)
    name = subj.name
    subj.delete()
    messages.success(request, f"Subject '{name}' deleted.")
    return redirect('subjects:subject_list')

@login_required
@admin_required
def structure_management(request):
    semesters = Semester.objects.all()
    sections = Section.objects.all()
    classrooms = Classroom.objects.all()
    academic_years = AcademicYear.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_academic_year':
            year_name = request.POST.get('year_name')
            is_current = request.POST.get('is_current') == 'on'
            if year_name:
                AcademicYear.objects.create(name=year_name, is_current=is_current)
                messages.success(request, f"Academic Year {year_name} added.")
        elif action == 'add_semester':
            sem_name = request.POST.get('sem_name')
            sem_num = request.POST.get('sem_number')
            ay_id = request.POST.get('academic_year')
            if sem_name and sem_num:
                ay = AcademicYear.objects.get(id=ay_id) if ay_id else None
                Semester.objects.create(name=sem_name, number=sem_num, academic_year=ay)
                messages.success(request, f"Semester {sem_name} added.")
        elif action == 'add_section':
            sec_name = request.POST.get('sec_name')
            capacity = request.POST.get('capacity', 60)
            if sec_name:
                Section.objects.create(name=sec_name, capacity=capacity)
                messages.success(request, f"Section {sec_name} added.")
        elif action == 'add_classroom':
            room_num = request.POST.get('room_number')
            bldg = request.POST.get('building_name')
            cap = request.POST.get('capacity', 60)
            if room_num:
                Classroom.objects.create(room_number=room_num, building_name=bldg, capacity=cap)
                messages.success(request, f"Classroom {room_num} added.")
        return redirect('subjects:structure')

    return render(request, 'subjects/structure.html', {
        'semesters': semesters,
        'sections': sections,
        'classrooms': classrooms,
        'academic_years': academic_years
    })
