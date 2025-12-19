from app.models import Question
print(f"Total questions: {Question.objects.count()}")
for q in Question.objects.all()[:10]:
    print(f"ID: {q.id}, Category: {q.category}, Module: {q.module}, Text: {q.question_text[:50]}")
