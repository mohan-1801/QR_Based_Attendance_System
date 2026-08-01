# Smart QR Code Attendance System - Production & Deployment Guide

A production-ready, highly secure **Smart QR Code Attendance System** built with **Python 3.x**, **Django 5.x**, **Bootstrap 5**, **Chart.js**, and **Django REST Framework**.

This repository is pre-configured for automated production deployment across **Render**, **Railway**, **PythonAnywhere**, **Ubuntu VPS (Nginx + Gunicorn)**, and **Docker**.

---

## 🚀 Supported Deployment Targets

| Deployment Target | Primary Config File | Static Files Handler | Database |
|---|---|---|---|
| **Render** | `render.yaml` | WhiteNoise | PostgreSQL |
| **Railway** | `railway.json`, `Procfile` | WhiteNoise | PostgreSQL |
| **Docker / Compose** | `Dockerfile`, `docker-compose.yml` | WhiteNoise | PostgreSQL Container |
| **Ubuntu VPS** | `deployment/nginx.conf`, `deployment/gunicorn.service` | Nginx Direct | PostgreSQL / SQLite |
| **PythonAnywhere** | `deployment/pythonanywhere_wsgi.py` | PythonAnywhere Static | MySQL / PostgreSQL / SQLite |

---

## 🛠️ Local Development & Quick Start

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/QR_Based_Attendance.git
cd QR_Based_Attendance
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run Migrations & Seed Database
```bash
python manage.py makemigrations accounts departments subjects faculty students attendance notifications dashboard reports api
python manage.py migrate
python seed_data.py
```

### 4. Launch Local Development Server
```bash
python manage.py runserver 8000
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Pre-Configured Demo Accounts

| Role | Username | Password | Features |
|---|---|---|---|
| **Super Admin** | `admin` | `admin123` | System management, Departments, Courses, Faculty & Student administration, Analytics |
| **Faculty** | `faculty` | `faculty123` | Generate live QR sessions, Live scanning feed, Manual attendance correction, Export PDF/Excel |
| **Student** | `student` | `student123` | Camera QR scanner, Attendance percentage, History timeline |

---

## ☁️ 1. Render Deployment (Primary)

The repository includes a ready-to-use `render.yaml` Blueprint spec.

1. Connect your repository to [Render.com](https://render.com/).
2. Click **New +** -> **Blueprint**.
3. Select this repository. Render will automatically detect `render.yaml` and provision:
   - A Web Service (`smart-qr-attendance`)
   - A PostgreSQL Database (`smart-qr-db`)
4. Set optional environment variables (`EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`) in the Render Dashboard.
5. Deployment will automatically execute build commands (`collectstatic`, `migrate`, `seed_data`) and start Gunicorn.

---

## 🚂 2. Railway Deployment

1. Create a new project on [Railway.app](https://railway.app/).
2. Select **Deploy from GitHub repo** and connect this repository.
3. Add a **PostgreSQL** database service in Railway.
4. Add Environment Variables in Railway Web Service:
   - `SECRET_KEY`: Generate a random secure key
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.railway.app,localhost`
   - `DATABASE_URL`: `${Postgres.DATABASE_URL}`
5. Railway will automatically detect `railway.json` and `Procfile` to deploy.

---

## 🐳 3. Docker & Docker Compose Deployment

Run the complete full-stack web application with PostgreSQL inside Docker containers:

```bash
# Build and start services in detached mode
docker-compose up -d --build

# Run migrations & seed data inside docker
docker-compose exec web python manage.py migrate
docker-compose exec web python seed_data.py

# Check running container logs
docker-compose logs -f web
```

Open `http://localhost:8000/` to access the application.

---

## 🌐 4. PythonAnywhere Deployment

1. Upload or `git clone` the repository to `/home/yourusername/QR_Based_Attendance`.
2. Create a virtual environment and install requirements:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 smart_qr_env
   pip install -r requirements.txt
   ```
3. Go to the **Web** tab on PythonAnywhere and create a new Web App (select Manual Configuration).
4. In the **WSGI configuration file** section, edit the file and paste the contents of [deployment/pythonanywhere_wsgi.py](file:///e:/QR_Based_Attendance/deployment/pythonanywhere_wsgi.py). Update `yourusername` with your account name.
5. In the **Static files** section:
   - URL: `/static/` -> Directory: `/home/yourusername/QR_Based_Attendance/staticfiles`
   - URL: `/media/` -> Directory: `/home/yourusername/QR_Based_Attendance/media`
6. Run `python manage.py collectstatic --noinput` in bash console.
7. Reload the web app.

---

## 🐧 5. Ubuntu VPS Deployment (Nginx + Gunicorn + SSL)

An automated deployment script is located at [deployment/vps_setup.sh](file:///e:/QR_Based_Attendance/deployment/vps_setup.sh).

### Manual Step-by-Step VPS Setup:

1. **Install Dependencies & Nginx**:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv nginx postgresql certbot python3-certbot-nginx
   ```

2. **Clone & Setup Virtualenv**:
   ```bash
   sudo mkdir -p /var/www/QR_Based_Attendance
   sudo chown -R $USER:$USER /var/www/QR_Based_Attendance
   git clone https://github.com/yourusername/QR_Based_Attendance.git /var/www/QR_Based_Attendance
   cd /var/www/QR_Based_Attendance
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment & Run Migrations**:
   ```bash
   cp .env.example .env
   # Edit .env with production database credentials
   python manage.py migrate
   python seed_data.py
   python manage.py collectstatic --noinput
   ```

4. **Enable Gunicorn Systemd Service**:
   ```bash
   sudo cp deployment/gunicorn.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

5. **Enable Nginx Reverse Proxy & SSL**:
   ```bash
   sudo cp deployment/nginx.conf /etc/nginx/sites-available/smart_qr
   sudo ln -s /etc/nginx/sites-available/smart_qr /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   
   # Enable free SSL certificate with Let's Encrypt
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## 🛡️ Production Security Checklist

- [x] **`DEBUG = False`** enforced in production settings.
- [x] **`SECRET_KEY`** loaded safely from environment.
- [x] **WhiteNoise** static asset compression & caching enabled.
- [x] **HTTPS Security Headers**: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS=31536000`, `X_FRAME_OPTIONS='DENY'`.
- [x] **Database SSL Connections**: Enforced with `dj-database-url`.
- [x] **Anti-CSRF & Anti-XSS**: Standard protection enabled on all dynamic endpoints.

---

## 💾 Database Backup and Restore

### PostgreSQL Backup
```bash
pg_dump -U qr_user -h localhost smart_qr_db > backup_smart_qr_$(date +%Y%m%d).sql
```

### PostgreSQL Restore
```bash
psql -U qr_user -h localhost -d smart_qr_db < backup_smart_qr_20260728.sql
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The repository includes [.github/workflows/ci.yml](file:///e:/QR_Based_Attendance/.github/workflows/ci.yml) which automatically:
- Runs security checks (`python manage.py check`)
- Tests database migrations & runs Django test suites
- Verifies static assets collection (`collectstatic`)
