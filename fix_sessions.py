import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satly.settings')
django.setup()

from app.models import ExamSession

# Cancel all break/in_progress sessions
sessions = ExamSession.objects.filter(status__in=['in_progress', 'break'])
count = sessions.count()
sessions.update(status='cancelled')
print(f"Cancelled {count} sessions")
