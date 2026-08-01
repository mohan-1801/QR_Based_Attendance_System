from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'faculty', views.FacultyViewSet, basename='faculty')
router.register(r'attendance', views.AttendanceRecordViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('qr/generate/', views.generate_qr_api, name='api_qr_generate'),
]
