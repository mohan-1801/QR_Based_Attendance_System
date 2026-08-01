from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:dashboard')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('departments/', include('apps.departments.urls', namespace='departments')),
    path('subjects/', include('apps.subjects.urls', namespace='subjects')),
    path('faculty/', include('apps.faculty.urls', namespace='faculty')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
    path('api/', include('apps.api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
