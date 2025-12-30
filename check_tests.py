import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'satly.settings'
django.setup()

from app.models import Test

tests = Test.objects.all()
for t in tests:
    q_count = len(t.test_questions) if t.test_questions else 0
    print(f'ID: {t.id}, Title: "{t.title}", Type: {t.test_type}, Q: {q_count}')
