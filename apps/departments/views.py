from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Course, Branch

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            messages.error(request, "Access restricted to administrators.")
            return redirect('dashboard:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
@admin_required
def department_list(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        description = request.POST.get('description')
        established_year = request.POST.get('established_year') or None
        if code and name:
            Department.objects.create(
                code=code, name=name, description=description, established_year=established_year
            )
            messages.success(request, f"Department '{name}' created successfully.")
            return redirect('departments:department_list')
    return render(request, 'departments/department_list.html', {'departments': departments})

@login_required
@admin_required
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    name = dept.name
    dept.delete()
    messages.success(request, f"Department '{name}' deleted successfully.")
    return redirect('departments:department_list')

@login_required
@admin_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    departments = Department.objects.all()
    if request.method == 'POST':
        department_id = request.POST.get('department')
        code = request.POST.get('code')
        name = request.POST.get('name')
        degree_type = request.POST.get('degree_type')
        duration_years = request.POST.get('duration_years', 4)
        if department_id and code and name:
            dept = get_object_or_404(Department, pk=department_id)
            Course.objects.create(
                department=dept, code=code, name=name, degree_type=degree_type, duration_years=duration_years
            )
            messages.success(request, f"Course '{name}' added successfully.")
            return redirect('departments:course_list')
    return render(request, 'departments/course_list.html', {'courses': courses, 'departments': departments})

@login_required
@admin_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    name = course.name
    course.delete()
    messages.success(request, f"Course '{name}' deleted.")
    return redirect('departments:course_list')
