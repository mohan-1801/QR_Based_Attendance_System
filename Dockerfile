# Production Dockerfile for Smart QR Code Attendance System
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (build tools, PostgreSQL client, libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY . /app/

# Collect static files during image build
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Run Gunicorn WSGI server
CMD ["gunicorn", "smart_qr_attendance.wsgi:application", "--config", "gunicorn.conf.py"]
