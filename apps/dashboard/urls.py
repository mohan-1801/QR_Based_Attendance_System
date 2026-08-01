from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_router, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
]
