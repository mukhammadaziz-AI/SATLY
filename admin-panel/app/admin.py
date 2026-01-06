from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin 
from .models import User, Question, ExamSession, ExamAnswer, Test, TestResult, DailyStats 
from .custom_admin import satly_admin_site 

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'subscription', 'status', 'best_score', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'status', 'subscription', 'english_level')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'telegram_username', 'english_level', 'avatar', 'subscription', 'status', 'best_score', 'target_score', 'tests_completed', 'total_time_spent')
        }),
    )

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'module', 'question_number', 'correct_answer', 'created_at')
    list_filter = ('category', 'module')
    search_fields = ('question_text',)
    ordering = ('category', 'module', 'question_number')

class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'current_section', 'total_score', 'started_at', 'completed_at')
    list_filter = ('status', 'current_section')
    search_fields = ('user__username', 'user__email')
    ordering = ('-started_at',)

class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam_session', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)

class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'test_type', 'difficulty', 'duration', 'is_active')
    list_filter = ('category', 'test_type', 'difficulty', 'is_active')
    search_fields = ('title', 'description')

class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'band_score', 'completed_at')
    list_filter = ('test__category',)
    search_fields = ('user__username', 'user__email')

class DailyStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'active_users', 'new_signups', 'tests_completed')
    ordering = ('-date',)

satly_admin_site.register(User, CustomUserAdmin)
satly_admin_site.register(Question, QuestionAdmin)
satly_admin_site.register(ExamSession, ExamSessionAdmin)
satly_admin_site.register(ExamAnswer, ExamAnswerAdmin)
satly_admin_site.register(Test, TestAdmin)
satly_admin_site.register(TestResult, TestResultAdmin)
satly_admin_site.register(DailyStats, DailyStatsAdmin)
