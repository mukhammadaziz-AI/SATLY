from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from app.models import User, Test, TestResult, DailyStats


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        User.objects.filter(is_superuser=False).delete()
        Test.objects.all().delete()
        TestResult.objects.all().delete()
        DailyStats.objects.all().delete()
        
        first_names = ['Ali', 'Vali', 'Sardor', 'Jasur', 'Bekzod', 'Dilshod', 'Anvar', 'Rustam', 'Shoxrux', 'Jamshid',
                       'Gulnora', 'Madina', 'Nilufar', 'Zarina', 'Kamila', 'Nodira', 'Shahzoda', 'Malika', 'Dilfuza', 'Sevinch']
        last_names = ['Karimov', 'Rahimov', 'Toshmatov', 'Ergashev', 'Umarov', 'Xolmatov', 'Saidov', 'Nazarov', 'Alimov', 'Boymatov']
        
        users = []
        for i in range(50):
            first = random.choice(first_names)
            last = random.choice(last_names)
            user = User.objects.create_user(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password='password123',
                first_name=first,
                last_name=last,
                phone=f'+998 9{random.randint(0,9)} {random.randint(100,999)} {random.randint(10,99)} {random.randint(10,99)}',
                subscription=random.choice(['free', 'free', 'free', 'premium', 'premium', 'enterprise']),
                status=random.choice(['active', 'active', 'active', 'active', 'inactive', 'suspended']),
                band_score=round(random.uniform(4.0, 9.0), 1),
                tests_completed=random.randint(0, 50),
                created_at=timezone.now() - timedelta(days=random.randint(0, 90))
            )
            users.append(user)
        
        self.stdout.write(f'Created {len(users)} users')
        
        test_data = [
            {'title': 'IELTS Reading Practice 1', 'category': 'english', 'test_type': 'reading', 'duration': 60, 'questions_count': 40},
            {'title': 'IELTS Listening Practice 1', 'category': 'english', 'test_type': 'listening', 'duration': 30, 'questions_count': 40},
            {'title': 'IELTS Writing Task 1', 'category': 'english', 'test_type': 'writing', 'duration': 20, 'questions_count': 1},
            {'title': 'IELTS Writing Task 2', 'category': 'english', 'test_type': 'writing', 'duration': 40, 'questions_count': 1},
            {'title': 'IELTS Speaking Mock Test', 'category': 'english', 'test_type': 'speaking', 'duration': 15, 'questions_count': 3},
            {'title': 'Advanced Reading Comprehension', 'category': 'english', 'test_type': 'reading', 'duration': 45, 'questions_count': 30},
            {'title': 'Vocabulary Builder Test', 'category': 'english', 'test_type': 'reading', 'duration': 30, 'questions_count': 50},
            {'title': 'Algebra Fundamentals', 'category': 'math', 'test_type': 'algebra', 'duration': 45, 'questions_count': 25},
            {'title': 'Geometry Basics', 'category': 'math', 'test_type': 'geometry', 'duration': 40, 'questions_count': 20},
            {'title': 'Calculus Introduction', 'category': 'math', 'test_type': 'calculus', 'duration': 60, 'questions_count': 15},
            {'title': 'SAT Math Practice', 'category': 'math', 'test_type': 'algebra', 'duration': 55, 'questions_count': 38},
            {'title': 'Advanced Geometry', 'category': 'math', 'test_type': 'geometry', 'duration': 50, 'questions_count': 25},
        ]
        
        tests = []
        for data in test_data:
            test = Test.objects.create(
                title=data['title'],
                description=f"Practice test for {data['test_type']}",
                category=data['category'],
                test_type=data['test_type'],
                difficulty=random.choice(['easy', 'medium', 'hard']),
                duration=data['duration'],
                questions_count=data['questions_count'],
                is_active=True
            )
            tests.append(test)
        
        self.stdout.write(f'Created {len(tests)} tests')
        
        for user in users:
            num_results = random.randint(0, 10)
            for _ in range(num_results):
                test = random.choice(tests)
                TestResult.objects.create(
                    user=user,
                    test=test,
                    score=round(random.uniform(40, 100), 1),
                    band_score=round(random.uniform(4.0, 9.0), 1),
                    time_spent=random.randint(test.duration * 30, test.duration * 60),
                    completed_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
        
        self.stdout.write(f'Created test results')
        
        today = timezone.now().date()
        for i in range(30):
            date = today - timedelta(days=i)
            DailyStats.objects.create(
                date=date,
                active_users=random.randint(50, 200),
                new_signups=random.randint(5, 30),
                tests_completed=random.randint(20, 100)
            )
        
        self.stdout.write(f'Created daily stats')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))
