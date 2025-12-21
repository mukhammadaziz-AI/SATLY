from app.models import Test
Test.objects.filter(title='gfsdgs').delete()
print("Deleted gfsdgs test")
