from app.models import Test
import json

tests = list(Test.objects.values('id', 'title', 'test_type', 'category'))
print(json.dumps(tests, indent=2))
