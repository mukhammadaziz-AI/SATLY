from app.models import Question
for category in ['english', 'math']:
    for module in [1, 2]:
        qs = Question.objects.filter(category=category, module=module)
        print(f"{category} module {module}: {qs.count()} questions")
        for q in qs[:2]:
            print(f"  Q{q.question_number}: {q.question_text[:100]}")
