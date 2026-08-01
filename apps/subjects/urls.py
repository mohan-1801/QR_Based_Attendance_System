from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/delete/<int:pk>/', views.delete_subject, name='delete_subject'),
    path('structure/', views.structure_management, name='structure'),
]
