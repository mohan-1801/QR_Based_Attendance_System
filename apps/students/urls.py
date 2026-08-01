from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('list/', views.student_list, name='student_list'),
    path('delete/<int:pk>/', views.delete_student, name='delete_student'),
    path('import-excel/', views.import_students_excel, name='import_excel'),
    path('export-excel/', views.export_students_excel, name='export_excel'),
    path('scan-qr/', views.scan_qr_page, name='scan_qr'),
    path('api/validate-qr/', views.validate_qr_api, name='validate_qr_api'),
    path('history/', views.student_history_view, name='history'),
]
