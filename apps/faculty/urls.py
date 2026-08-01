from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('list/', views.faculty_list, name='faculty_list'),
    path('delete/<int:pk>/', views.delete_faculty, name='delete_faculty'),
    path('generate-qr/', views.generate_qr_view, name='generate_qr'),
    path('live-session/<uuid:session_id>/', views.live_session_view, name='live_session'),
    path('stop-session/<uuid:session_id>/', views.stop_session_view, name='stop_session'),
    path('api/live-data/<uuid:session_id>/', views.live_session_data_api, name='live_data_api'),
    path('manual-attendance/', views.manual_attendance_view, name='manual_attendance'),
    path('export/pdf/<uuid:session_id>/', views.export_session_pdf, name='export_session_pdf'),
    path('export/excel/<uuid:session_id>/', views.export_session_excel, name='export_session_excel'),
]
