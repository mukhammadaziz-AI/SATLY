import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satly.settings')
django.setup()

from app.models import User

# Delete existing admin if exists
User.objects.filter(username='admin').delete()

# Create new admin
user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print('Admin yaratildi!')
print('Username: admin')
print('Password: admin123')
