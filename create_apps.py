import os

apps = ['accounts', 'departments', 'subjects', 'faculty', 'students', 'attendance', 'notifications', 'dashboard', 'reports', 'api']
os.makedirs('apps', exist_ok=True)
with open('apps/__init__.py', 'w') as f:
    pass

for app in apps:
    app_dir = os.path.join('apps', app)
    os.makedirs(app_dir, exist_ok=True)
    
    with open(os.path.join(app_dir, '__init__.py'), 'w') as f:
        pass
        
    class_name = "".join(x.capitalize() for x in app.split('_'))
    with open(os.path.join(app_dir, 'apps.py'), 'w') as f:
        f.write(f'from django.apps import AppConfig\n\nclass {class_name}Config(AppConfig):\n    default_auto_field = "django.db.models.BigAutoField"\n    name = "apps.{app}"\n')
        
    with open(os.path.join(app_dir, 'models.py'), 'w') as f:
        f.write('from django.db import models\n')
        
    with open(os.path.join(app_dir, 'views.py'), 'w') as f:
        f.write('from django.shortcuts import render\n')
        
    with open(os.path.join(app_dir, 'admin.py'), 'w') as f:
        f.write('from django.contrib import admin\n')
        
    with open(os.path.join(app_dir, 'urls.py'), 'w') as f:
        f.write(f'from django.urls import path\n\napp_name = "{app}"\n\nurlpatterns = []\n')

print("Apps created successfully!")
