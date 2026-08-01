from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('departments/', views.department_list, name='department_list'),
    path('departments/delete/<int:pk>/', views.delete_department, name='delete_department'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/delete/<int:pk>/', views.delete_course, name='delete_course'),
]
