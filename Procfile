web: gunicorn smart_qr_attendance.wsgi:application --config gunicorn.conf.py
release: python manage.py migrate && python manage.py collectstatic --noinput
