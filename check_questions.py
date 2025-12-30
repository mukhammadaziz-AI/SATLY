from app.models import Question
import json

questions = list(Question.objects.values('category', 'module', 'question_text'))
print(json.dumps(questions, indent=2))
