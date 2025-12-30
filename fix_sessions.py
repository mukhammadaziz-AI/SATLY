import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'satly.settings'
django.setup()

from app.models import ExamSession
from django.utils import timezone

sessions = ExamSession.objects.filter(status='break')
for s in sessions:
    s.status = 'completed'
    s.completed_at = timezone.now()
    s.total_score = s.english_score or 0
    s.save()
    print(f'Fixed session {s.id}')
