import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'satly.settings'
django.setup()

from app.models import ExamSession, ExamAnswer
sessions = ExamSession.objects.all().order_by('-started_at')[:5]
for s in sessions:
    print(f'Session {s.id}: status={s.status}, section={s.current_section}, module={s.current_module}, test={s.test_id}')
    answers = ExamAnswer.objects.filter(exam_session=s).count()
    print(f'  Answers: {answers}')
