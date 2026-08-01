#!/bin/bash
# Ubuntu 22.04 / 24.04 VPS Automated Deployment Script for Smart QR System

set -e

echo "=== Updating System Packages ==="
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx ufw

echo "=== Setting up Firewall (UFW) ==="
sudo ufw allow 'Nginx Full'
sudo ufw allow 22/tcp
sudo ufw --force enable

echo "=== Creating Project Virtual Environment ==="
sudo mkdir -p /var/www/QR_Based_Attendance
sudo chown -R $USER:$USER /var/www/QR_Based_Attendance

cd /var/www/QR_Based_Attendance
python3 -m venv venv
source venv/bin/venv/activate || source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "=== Running Migrations & Collecting Static Files ==="
python manage.py makemigrations accounts departments subjects faculty students attendance notifications dashboard reports api
python manage.py migrate
python seed_data.py
python manage.py collectstatic --noinput

echo "=== Configuring Gunicorn Systemd Service ==="
sudo cp deployment/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "=== Configuring Nginx ==="
sudo cp deployment/nginx.conf /etc/nginx/sites-available/smart_qr
sudo ln -sf /etc/nginx/sites-available/smart_qr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "=== VPS Deployment Setup Complete! ==="
