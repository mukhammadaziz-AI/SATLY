from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    
    ENGLISH_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('elementary', 'Elementary'),
        ('intermediate', 'Intermediate'),
        ('upper_intermediate', 'Upper Intermediate'),
        ('advanced', 'Advanced'),
        ('ielts_5', 'IELTS 5.0'),
        ('ielts_5.5', 'IELTS 5.5'),
        ('ielts_6', 'IELTS 6.0'),
        ('ielts_6.5', 'IELTS 6.5'),
        ('ielts_7', 'IELTS 7.0+'),
        ('b1', 'B1'),
        ('b2', 'B2'),
        ('c1', 'C1'),
    ]
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    telegram_username = models.CharField(max_length=100, blank=True, null=True)
    english_level = models.CharField(max_length=50, choices=ENGLISH_LEVEL_CHOICES, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    subscription = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    best_score = models.IntegerField(default=0)
    target_score = models.IntegerField(default=1500)
    tests_completed = models.IntegerField(default=0)
    total_time_spent = models.IntegerField(default=0, help_text="Total time spent in minutes")
    created_at = models.DateTimeField(default=timezone.now)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.email or self.username


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('english', 'English'),
        ('math', 'Math'),
    ]
    
    MODULE_CHOICES = [
        (1, 'Module 1'),
        (2, 'Module 2'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    module = models.IntegerField(choices=MODULE_CHOICES)
    question_number = models.IntegerField()
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_answer = models.CharField(max_length=1)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['category', 'module', 'question_number']
        unique_together = ['category', 'module', 'question_number']
    
    def __str__(self):
        return f"{self.category} - Module {self.module} - Q{self.question_number}"


class ExamSession(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('break', 'Break'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    certificate_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    current_section = models.CharField(max_length=20, default='english')
    current_module = models.IntegerField(default=1)
    english_module1_score = models.IntegerField(default=0)
    english_module2_score = models.IntegerField(default=0)
    math_module1_score = models.IntegerField(default=0)
    math_module2_score = models.IntegerField(default=0)
    english_score = models.IntegerField(default=0)
    math_score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'exam_sessions'
        ordering = ['-started_at']
    
    def save(self, *args, **kwargs):
        if not self.certificate_id and self.status == 'completed':
            self.certificate_id = f"SATLY-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.started_at.strftime('%Y-%m-%d')}"


class ExamAnswer(models.Model):
    exam_session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exam_answers'
        unique_together = ['exam_session', 'question']
    
    def __str__(self):
        return f"{self.exam_session} - Q{self.question.question_number}"


class Test(models.Model):
    CATEGORY_CHOICES = [
        ('english', 'English'),
        ('math', 'Math'),
    ]
    
    TYPE_CHOICES = [
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('math_module1', 'Math Module 1'),
        ('math_module2', 'Math Module 2'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    test_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    duration = models.IntegerField(help_text="Duration in minutes")
    questions_count = models.IntegerField(default=0)
    test_questions = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tests'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    score = models.DecimalField(max_digits=4, decimal_places=1)
    band_score = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    time_spent = models.IntegerField(help_text="Time spent in seconds")
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'test_results'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.score}"


class DailyStats(models.Model):
    date = models.DateField(unique=True)
    active_users = models.IntegerField(default=0)
    new_signups = models.IntegerField(default=0)
    tests_completed = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'daily_stats'
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('uzcard', 'Uzcard/Humo'),
        ('click', 'Click'),
        ('payme', 'Payme'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    card_number = models.CharField(max_length=16, blank=True, null=True)
    card_expiry = models.CharField(max_length=5, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=[('exam', 'Exam'), ('subscription', 'Subscription')], default='exam')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_method} - {self.amount} UZS"


class PricingSettings(models.Model):
    exam_price = models.DecimalField(max_digits=10, decimal_places=2, default=19999.00, help_text="Exam test narxi (so'm)")
    subscription_price = models.DecimalField(max_digits=10, decimal_places=2, default=49999.00, help_text="Oylik subscription narxi (so'm)")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pricing_settings'
    
    def __str__(self):
        return f"Exam: {self.exam_price} so'm, Subscription: {self.subscription_price} so'm"
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(id=1)
        return settings