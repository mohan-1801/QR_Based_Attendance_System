from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('api/chart-data/', views.chart_analytics_api, name='chart_data_api'),
    path('export/pdf/', views.export_filtered_pdf, name='export_pdf'),
    path('export/excel/', views.export_filtered_excel, name='export_excel'),
]
