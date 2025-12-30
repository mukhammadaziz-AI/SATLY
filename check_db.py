import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'satly.settings')
django.setup()

from app.models import Test, ExamSession

print("=== TESTS ===")
tests = Test.objects.all()
print(f"Total tests: {tests.count()}")
for t in tests:
    q_count = len(t.test_questions or [])
    print(f"  {t.id}: {t.title} - {t.test_type} - {q_count} questions")

print("\n=== ACTIVE EXAM SESSIONS ===")
sessions = ExamSession.objects.filter(status__in=['in_progress', 'break'])
print(f"Total active sessions: {sessions.count()}")
for s in sessions:
    test_info = f"{s.test.title} ({s.test.test_type})" if s.test else "No test"
    print(f"  {s.id}: User {s.user.email} - {s.status} - {test_info}")
