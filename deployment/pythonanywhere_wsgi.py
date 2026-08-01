# PythonAnywhere WSGI Configuration File
import os
import sys

# Path to project directory on PythonAnywhere
path = '/home/yourusername/QR_Based_Attendance'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'smart_qr_attendance.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
