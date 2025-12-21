import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satly.settings')
django.setup()

from app.models import Test
deleted_count, _ = Test.objects.filter(title='gfsdgs').delete()
print(f"Deleted {deleted_count} tests.")
