from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import json
import random

from .models import User, Test, TestResult, DailyStats, Question, ExamSession, ExamAnswer, Payment, PricingSettings


def calculate_section_score(correct_count, total_questions):
    if total_questions == 0:
        return 200
    # Simple SAT-like scaling: 200 to 800
    score = 200 + (correct_count / total_questions) * 600
    return int(score)


def update_user_stats(user, session):
    user.tests_completed += 1
    if session.total_score > user.best_score:
        user.best_score = session.total_score
    
    # Calculate time spent in minutes
    time_mins = session.time_spent // 60
    user.total_time_spent += time_mins
    user.save()
    
    # Update daily stats
    today = timezone.now().date()
    stats, created = DailyStats.objects.get_or_create(date=today)
    stats.tests_completed += 1
    stats.save()



def home_page(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    return render(request, 'main/index.html')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                auth_login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    
    return render(request, 'main/auth.html', {'mode': 'login'})


def register_page(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        phone = request.POST.get('phone', '').strip()
        telegram = request.POST.get('telegram', '').strip()
        english_level = request.POST.get('english_level', '')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'main/auth.html', {'mode': 'register'})
        
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        username = email.split('@')[0] + str(random.randint(100, 999))
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            telegram_username=telegram,
            english_level=english_level
        )
        
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Account created successfully!')
        return redirect('user_dashboard')
    
    return render(request, 'main/auth.html', {'mode': 'register'})


@csrf_exempt
def quick_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        telegram = request.POST.get('telegram', '').strip()
        english_level = request.POST.get('english_level', '')
        
        request.session['quick_register'] = {
            'full_name': full_name,
            'phone': phone,
            'telegram': telegram,
            'english_level': english_level
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Information saved! Please complete your registration.',
            'redirect': '/register/'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


@login_required
def user_dashboard(request):
    user = request.user
    recent_results = ExamSession.objects.filter(user=user, status='completed').order_by('-completed_at')[:5]
    
    # Fetch available tests from Test model and group by title
    all_tests = Test.objects.filter(is_active=True).order_by('-created_at')
    grouped_tests = {}
    for test in all_tests:
        if test.title not in grouped_tests:
            grouped_tests[test.title] = {
                'title': test.title,
                'english': None,
                'math': None,
                'total_questions': 0,
                'total_duration': 0,
                'id': test.id,
                'category': test.category, # For styling
                'description': test.description
            }
        
        if test.category == 'english':
            grouped_tests[test.title]['english'] = test
            grouped_tests[test.title]['id'] = test.id
            grouped_tests[test.title]['category'] = 'english'
        elif test.category == 'math':
            grouped_tests[test.title]['math'] = test
            if not grouped_tests[test.title]['english']:
                grouped_tests[test.title]['id'] = test.id
                grouped_tests[test.title]['category'] = 'math'
        
        grouped_tests[test.title]['total_questions'] += test.questions_count
        grouped_tests[test.title]['total_duration'] += test.duration
    
    available_tests = grouped_tests.values()
    
    total_time = sum([
        exam.time_spent for exam in ExamSession.objects.filter(user=user, status='completed')
    ])
    total_minutes = total_time // 60
    hours = total_minutes // 60
    mins = total_minutes % 60
    total_time_display = f"{hours}h {mins}m"
    
    return render(request, 'main/dashboard.html', {
        'user': user,
        'recent_results': recent_results,
        'available_tests': available_tests,
        'total_time_display': total_time_display
    })


@login_required
def user_progress(request):
    user = request.user
    exam_sessions = ExamSession.objects.filter(user=user, status='completed').order_by('-completed_at')
    
    if not exam_sessions.exists():
        return render(request, 'main/progress.html', {
            'no_results': True,
            'user': user
        })
    
    scores_data = []
    for exam in exam_sessions[:10]:
        scores_data.append({
            'date': exam.completed_at.strftime('%b %d'),
            'total': exam.total_score,
            'english': exam.english_score,
            'math': exam.math_score
        })
    
    avg_score = exam_sessions.aggregate(avg=Avg('total_score'))['avg'] or 0
    best_score = user.best_score
    total_tests = exam_sessions.count()
    
    return render(request, 'main/progress.html', {
        'user': user,
        'exam_sessions': exam_sessions,
        'scores_data': json.dumps(list(reversed(scores_data))),
        'avg_score': round(avg_score),
        'best_score': best_score,
        'total_tests': total_tests,
        'no_results': False
    })


@login_required
def user_settings(request):
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        telegram = request.POST.get('telegram', '').strip()
        english_level = request.POST.get('english_level', '')
        target_score = request.POST.get('target_score', '')
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.phone = phone
        user.telegram_username = telegram
        if english_level:
            user.english_level = english_level
        if target_score:
            user.target_score = int(target_score)
        
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, "Ma'lumotlaringiz muvaffaqiyatli saqlandi!")
        return redirect('user_settings')
    
    return render(request, 'main/settings.html', {'user': user})


@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        request.user.avatar = request.FILES['avatar']
        request.user.save()
    return redirect('user_dashboard')


@login_required
def start_exam(request):
    # Enforce payment for non-premium users
    has_paid = request.session.get('has_paid_for_attempt', False)
    if request.user.subscription != 'premium' and not has_paid:
        # Check if there's an active session already - if so, allow it
        if not ExamSession.objects.filter(user=request.user, status__in=['in_progress', 'break']).exists():
            return redirect('payment_page')

    # Check if a session is already in progress
    session = ExamSession.objects.filter(user=request.user, status__in=['in_progress', 'break']).first()
    
    # Check for test_id in session (passed from payment_page) or from GET
    test_id = request.session.get('pending_test_id') or request.GET.get('test_id')
    
    if not session:
        # If no session and no test_id provided, show test selection list
        if not test_id:
            available_tests_raw = Test.objects.filter(is_active=True).order_by('-created_at')
            grouped_tests = {}
            for test in available_tests_raw:
                if test.title not in grouped_tests:
                    grouped_tests[test.title] = {
                        'title': test.title,
                        'english': None,
                        'math': None,
                        'total_questions': 0,
                        'total_duration': 0,
                        'id': test.id,
                        'category': test.category,
                        'description': test.description
                    }
                if test.category == 'english':
                    grouped_tests[test.title]['english'] = test
                    grouped_tests[test.title]['id'] = test.id
                    grouped_tests[test.title]['category'] = 'english'
                elif test.category == 'math':
                    grouped_tests[test.title]['math'] = test
                    if not grouped_tests[test.title]['english']:
                        grouped_tests[test.title]['id'] = test.id
                        grouped_tests[test.title]['category'] = 'math'
                
                grouped_tests[test.title]['total_questions'] += test.questions_count
                grouped_tests[test.title]['total_duration'] += test.duration
            
            return render(request, 'main/exam.html', {
                'is_selection_mode': True, 
                'available_tests': grouped_tests.values(),
                'has_paid': has_paid
            })
        
        # Clear payment flags once we start creating a session
        if 'pending_test_id' in request.session:
            del request.session['pending_test_id']
        if 'has_paid_for_attempt' in request.session:
            del request.session['has_paid_for_attempt']
            
        test = get_object_or_404(Test, id=test_id)
        
        # If they chose a Math test, but it belongs to a full test pair, start with English
        if test.category == 'math':
            eng_test = Test.objects.filter(title=test.title, category='english', is_active=True).first()
            if eng_test:
                test = eng_test

        session = ExamSession.objects.create(user=request.user, test=test, current_section=test.category)
        session.save()
    
    # If session is in break status, redirect to break page (which is handled in exam.html)
    
    # Determine questions based on whether it's a linked Test or generic Question bank
    if session.test:
        test_questions = session.test.test_questions
        questions = []
        for i, q in enumerate(test_questions):
            # Map options from array to fields if needed
            options_data = q.get('options', [])
            opt_a = q.get('option_a', '')
            opt_b = q.get('option_b', '')
            opt_c = q.get('option_c', '')
            opt_d = q.get('option_d', '')

            if options_data:
                for opt in options_data:
                    label = opt.get('label', '').upper()
                    if label == 'A': opt_a = opt.get('text', '')
                    elif label == 'B': opt_b = opt.get('text', '')
                    elif label == 'C': opt_c = opt.get('text', '')
                    elif label == 'D': opt_d = opt.get('text', '')

            questions.append({
                'id': i, # Use index as ID for JSON questions
                'question_text': q.get('question_text', q.get('text', '')),
                'option_a': opt_a,
                'option_b': opt_b,
                'option_c': opt_c,
                'option_d': opt_d,
                'image': q.get('image', None)
            })
        time_remaining = session.test.duration * 60
    else:
        # Bank questions logic
        if session.current_section == 'english':
            questions = list(Question.objects.filter(
                category__iexact='english',
                module=session.current_module
            ).values('id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d'))
            time_remaining = 32 * 60
        else:
            questions = list(Question.objects.filter(
                category__iexact='math',
                module=session.current_module
            ).values('id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d'))
            time_remaining = 35 * 60

    existing_answers = ExamAnswer.objects.filter(exam_session=session)
    
    if session.test:
        # Check if we have answers for the CURRENT test (section)
        # We need to distinguish between English and Math answers if they are in the same session
        # Use question_index + section prefix or just question_index?
        # Let's use question_index but filtered by some logic
        # Actually, let's just clear answers for the new section if needed, or keep them if they are unique
        answer_dict = {str(ans.question_index): ans.selected_answer for ans in existing_answers if (ans.question_index is not None)}
    else:
        answer_dict = {str(ans.question_id): ans.selected_answer for ans in existing_answers}
    
    answers = [answer_dict.get(str(i), None) for i, _ in enumerate(questions)]
    
    section_title = session.test.title if session.test else f"{session.current_section.title()} Module {session.current_module}"
    if session.test:
        section_title += f" ({session.test.category.title()})"
    
    return render(request, 'main/exam.html', {
        'exam_session': session,
        'questions': json.dumps(questions),
        'answers': json.dumps(answers),
        'time_remaining': time_remaining,
        'section_title': section_title,
        'show_break': session.status == 'break'
    })


def generate_sample_questions(category, module):
    questions = []
    num_questions = 27 if category == 'english' else 22
    
    for i in range(1, num_questions + 1):
        q, created = Question.objects.get_or_create(
            category=category,
            module=module,
            question_number=i,
            defaults={
                'question_text': f'Sample {category.title()} Question {i}: Which of the following best describes the main idea?',
                'option_a': 'The author argues for environmental protection',
                'option_b': 'The passage discusses historical events',
                'option_c': "Technology's impact on society",
                'option_d': 'Economic development strategies',
                'correct_answer': random.choice(['A', 'B', 'C', 'D'])
            }
        )
        questions.append({
            'id': q.id,
            'question_text': q.question_text,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d
        })
    
    return questions


@csrf_exempt
@login_required
def api_save_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question_id = data.get('question_id') # This is the index for Test-based exams
        answer = data.get('answer')
        
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        
        if session.test:
            # For specific tests, question_id is the index in the JSON list
            try:
                question_index = int(question_id)
                test_questions = session.test.test_questions
                if 0 <= question_index < len(test_questions):
                    q_data = test_questions[question_index]
                    # Check both possible keys for correct answer
                    correct_answer = q_data.get('correct_answer', q_data.get('answer', ''))
                    
                    exam_answer, created = ExamAnswer.objects.update_or_create(
                        exam_session=session,
                        question_index=question_index,
                        category=session.current_section,
                        defaults={
                            'selected_answer': answer,
                            'is_correct': answer == correct_answer
                        }
                    )
                    return JsonResponse({'success': True})
            except (ValueError, TypeError):
                pass
        else:
            # Default behavior for bank questions
            question = get_object_or_404(Question, id=question_id)
            exam_answer, created = ExamAnswer.objects.update_or_create(
                exam_session=session,
                question=question,
                category=session.current_section,
                defaults={
                    'selected_answer': answer,
                    'is_correct': answer == question.correct_answer
                }
            )
            return JsonResponse({'success': True})
            
    return JsonResponse({'success': False})


@csrf_exempt
@login_required
def api_save_time(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        time_spent = data.get('time_spent', 0)
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        session.time_spent = time_spent
        session.save(update_fields=['time_spent'])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
@login_required
def api_finish_section(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        
        if session.test:
            # Scoring for the CURRENT section (English or Math)
            correct_count = ExamAnswer.objects.filter(
                exam_session=session,
                category=session.current_section,
                is_correct=True
            ).count()
            
            total_questions = len(session.test.test_questions) or 1
            section_score = calculate_section_score(correct_count, total_questions)
            
            if session.current_section == 'english':
                session.english_module1_score = correct_count
                session.english_score = section_score
                
                # Check if there is a Math version of this test
                math_test = Test.objects.filter(title=session.test.title, category='math', is_active=True).first()
                if math_test:
                    session.status = 'break'
                    session.save()
                    return JsonResponse({'next_action': 'break'})
            else:
                # Math section
                session.math_module1_score = correct_count
                session.math_score = section_score
            
            session.total_score = session.english_score + session.math_score
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()
            
            update_user_stats(request.user, session)
            return JsonResponse({'next_action': 'results'})
        else:
            # Default behavior for bank questions (unchanged)
            correct_count = ExamAnswer.objects.filter(
                exam_session=session,
                question__category=session.current_section,
                question__module=session.current_module,
                is_correct=True
            ).count()
            
            if session.current_section == 'english':
                if session.current_module == 1:
                    session.english_module1_score = correct_count
                    session.current_module = 2
                    session.save()
                    return JsonResponse({'next_action': 'next_module'})
                else:
                    session.english_module2_score = correct_count
                    session.english_score = calculate_section_score(
                        session.english_module1_score + session.english_module2_score, 54
                    )
                    session.current_section = 'math'
                    session.current_module = 1
                    session.status = 'break'
                    session.save()
                    return JsonResponse({'next_action': 'break'})
            else:
                if session.current_module == 1:
                    session.math_module1_score = correct_count
                    session.current_module = 2
                    session.save()
                    return JsonResponse({'next_action': 'next_module'})
                else:
                    session.math_module2_score = correct_count
                    session.math_score = calculate_section_score(
                        session.math_module1_score + session.math_module2_score, 44
                    )
                    session.total_score = session.english_score + session.math_score
                    session.status = 'completed'
                    session.completed_at = timezone.now()
                    session.save()
                    
                    update_user_stats(request.user, session)
                    return JsonResponse({'next_action': 'results'})
    
    return JsonResponse({'success': False})


@csrf_exempt
@login_required
def api_start_math(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        session = get_object_or_404(ExamSession, id=session_id, user=request.user)
        
        if session.test and session.current_section == 'english':
            # Find the Math version of the test
            math_test = Test.objects.filter(title=session.test.title, category='math', is_active=True).first()
            if math_test:
                session.test = math_test
                session.current_section = 'math'
        
        session.status = 'in_progress'
        session.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def exam_result(request, session_id):
    exam = get_object_or_404(ExamSession, id=session_id, user=request.user, status='completed')
    
    # Calculate duration
    if exam.completed_at and exam.started_at:
        duration = exam.completed_at - exam.started_at
        hours = duration.seconds // 3600
        mins = (duration.seconds % 3600) // 60
        exam_duration = f"{hours}h {mins}m"
    else:
        hours = exam.time_spent // 3600
        mins = (exam.time_spent % 3600) // 60
        exam_duration = f"{hours}h {mins}m"
    
    if exam.test:
        # For specific tests (including grouped ones)
        # english_module1_score stores English correct count
        # math_module1_score stores Math correct count
        english_correct = exam.english_module1_score
        math_correct = exam.math_module1_score
        
        # Determine total questions for each section to calculate "Test Scores" (10-40 scale)
        # This is a bit tricky since we only have the current test linked
        # Let's find both tests if grouped
        grouped_tests = Test.objects.filter(title=exam.test.title)
        eng_test = grouped_tests.filter(category='english').first()
        math_test = grouped_tests.filter(category='math').first()
        
        eng_total = len(eng_test.test_questions) if eng_test else 1
        math_total = len(math_test.test_questions) if math_test else 1
    else:
        # Generic bank exam
        english_correct = exam.english_module1_score + exam.english_module2_score
        math_correct = exam.math_module1_score + exam.math_module2_score
        eng_total = 54
        math_total = 44
    
    # SAT scale mapping (approximate)
    reading_score = round(10 + (english_correct / eng_total) * 30)
    writing_score = round(10 + (english_correct / eng_total) * 30) # Shared for English
    math_test_score = round(10 + (math_correct / math_total) * 30)
    
    # Percentiles (approximate)
    if exam.total_score >= 1550:
        english_percentile = 99
        user_percentile = 99
    elif exam.total_score >= 1400:
        english_percentile = 95
        user_percentile = 94
    elif exam.total_score >= 1200:
        english_percentile = 80
        user_percentile = 78
    elif exam.total_score >= 1000:
        english_percentile = 55
        user_percentile = 52
    else:
        english_percentile = 30
        user_percentile = 28
    
    return render(request, 'main/result.html', {
        'exam': exam,
        'user': request.user,
        'exam_duration': exam_duration,
        'reading_score': reading_score,
        'writing_score': writing_score,
        'math_test_score': math_test_score,
        'english_percentile': english_percentile,
        'user_percentile': user_percentile
    })


@staff_member_required(login_url='/django-admin/login/')
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')


@staff_member_required(login_url='/django-admin/login/')
def user_management(request):
    return render(request, 'admin/users.html')


@staff_member_required(login_url='/django-admin/login/')
def test_management(request):
    return render(request, 'admin/tests.html')


@staff_member_required(login_url='/django-admin/login/')
def results_page(request):
    return render(request, 'admin/results.html')


@staff_member_required(login_url='/django-admin/login/')
def settings_page(request):
    return render(request, 'admin/settings.html')


@csrf_exempt
@require_http_methods(["GET"])
def api_dashboard_stats(request):
    total_users = User.objects.filter(is_staff=False).count()
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    new_signups = User.objects.filter(is_staff=False, created_at__date__gte=week_ago).count()
    dau = User.objects.filter(is_staff=False, last_active__date=today).count()
    total_tests = ExamSession.objects.filter(status='completed').count()
    
    return JsonResponse({
        'total_users': total_users,
        'new_signups': new_signups,
        'dau': dau,
        'total_tests': total_tests,
    })


@csrf_exempt
@require_http_methods(["GET"])
def api_daily_active_users(request):
    days = request.GET.get('days', '7')
    end_date = timezone.now().date()
    
    if days == 'all':
        start_date = User.objects.filter(is_staff=False).order_by('created_at').first()
        if start_date:
            start_date = start_date.created_at.date()
        else:
            start_date = end_date - timedelta(days=30)
    else:
        days = int(days)
        start_date = end_date - timedelta(days=days-1)
    
    data = []
    current_date = start_date
    while current_date <= end_date:
        active_count = User.objects.filter(
            is_staff=False,
            last_active__date=current_date
        ).count()
        data.append({
            'date': current_date.strftime('%b %d'),
            'active_users': active_count
        })
        current_date += timedelta(days=1)
    
    return JsonResponse({'data': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_tests_completed(request):
    days = request.GET.get('days', '7')
    end_date = timezone.now().date()
    
    if days == 'all':
        first_session = ExamSession.objects.filter(status='completed').order_by('completed_at').first()
        if first_session and first_session.completed_at:
            start_date = first_session.completed_at.date()
        else:
            start_date = end_date - timedelta(days=30)
    else:
        days = int(days)
        start_date = end_date - timedelta(days=days-1)
    
    data = []
    current_date = start_date
    while current_date <= end_date:
        tests_count = ExamSession.objects.filter(
            status='completed',
            completed_at__date=current_date
        ).count()
        data.append({
            'date': current_date.strftime('%b %d'),
            'tests_completed': tests_count
        })
        current_date += timedelta(days=1)
    
    return JsonResponse({'data': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_top_band_scores(request):
    limit = int(request.GET.get('limit', 10))
    
    users = User.objects.filter(best_score__gt=0).order_by('-best_score')[:limit]
    
    data = [{
        'rank': i,
        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'band_score': user.best_score,
        'tests_completed': user.tests_completed
    } for i, user in enumerate(users, 1)]
    
    return JsonResponse({'data': data})


@csrf_exempt
@require_http_methods(["GET"])
def api_pricing(request):
    """Get current pricing for admin panel"""
    settings = PricingSettings.get_settings()
    return JsonResponse({
        'exam_price': str(settings.exam_price),
        'subscription_price': str(settings.subscription_price),
    })


@csrf_exempt
@require_http_methods(["GET"])
def api_admin_users(request):
    """Get all users with detailed stats for admin panel"""
    users = User.objects.filter(is_staff=False).select_related().annotate(
        total_tests_taken=Count('exam_sessions', filter=Q(exam_sessions__status='completed')),
        avg_band_score=Avg('exam_sessions__total_score', filter=Q(exam_sessions__status='completed'))
    ).order_by('-created_at')
    
    users_data = []
    for user in users:
        full_name = f"{user.first_name} {user.last_name}".strip() or 'No name'
        has_active_subscription = user.subscription == 'premium'
        
        users_data.append({
            'id': user.id,
            'full_name': full_name,
            'email': user.email,
            'phone_number': user.phone or '',
            'has_active_subscription': has_active_subscription,
            'avg_band_score': round(user.avg_band_score or 0, 1),
            'total_tests_taken': user.total_tests_taken,
            'date_joined': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        })
    
    return JsonResponse({'users': users_data})


@csrf_exempt
@require_http_methods(["GET"])
def api_admin_user_detail(request, user_id):
    """Get detailed user information"""
    user = get_object_or_404(User, id=user_id)
    
    total_tests = ExamSession.objects.filter(user=user, status='completed').count()
    avg_score = ExamSession.objects.filter(user=user, status='completed').aggregate(
        avg=Avg('total_score')
    )['avg'] or 0
    
    return JsonResponse({
        'id': user.id,
        'full_name': f"{user.first_name} {user.last_name}".strip() or 'No name',
        'email': user.email,
        'phone_number': user.phone or '',
        'has_active_subscription': user.subscription == 'premium',
        'avg_band_score': round(avg_score, 1),
        'total_tests_taken': total_tests,
        'date_joined': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
    })


@csrf_exempt
@require_http_methods(["DELETE"])
def api_admin_user_delete(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id, is_staff=False)
    user.delete()
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["GET"])
def api_users_list(request):
    status_filter = request.GET.get('status', 'all')
    subscription_filter = request.GET.get('subscription', 'all')
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if status_filter != 'all':
        users = users.filter(status=status_filter)
    
    if subscription_filter != 'all':
        users = users.filter(subscription=subscription_filter)
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.order_by('-created_at')[:100]
    
    data = [{
        'id': user.id,
        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'email': user.email,
        'phone': user.phone or '-',
        'subscription': user.subscription,
        'status': user.status,
        'band_score': user.best_score,
        'tests_completed': user.tests_completed,
        'created_at': user.created_at.strftime('%Y-%m-%d'),
        'last_active': user.last_active.strftime('%Y-%m-%d %H:%M') if user.last_active else '-',
    } for user in users]
    
    return JsonResponse({'data': data})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_user_detail(request, user_id):
    if request.method == "GET":
        user = get_object_or_404(User, id=user_id)
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'subscription': user.subscription,
            'status': user.status,
            'band_score': user.best_score,
            'tests_completed': user.tests_completed,
        })
    
    elif request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        data = json.loads(request.body)
        
        for field in ['status', 'subscription', 'first_name', 'last_name', 'phone']:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["GET"])
def api_tests_list(request):
    category = request.GET.get('category', 'all')
    
    tests = Test.objects.all()
    
    if category != 'all':
        tests = tests.filter(category=category)
    
    data = []
    for test in tests:
        completions = TestResult.objects.filter(test=test).count()
        avg_score = TestResult.objects.filter(test=test).aggregate(avg=Avg('score'))['avg']
        
        data.append({
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'category': test.category,
            'test_type': test.test_type,
            'difficulty': test.difficulty,
            'duration': test.duration,
            'questions_count': test.questions_count,
            'questions': test.test_questions,
            'is_active': test.is_active,
            'completions': completions,
            'avg_score': round(avg_score, 1) if avg_score else 0,
            'created_at': test.created_at.strftime('%Y-%m-%d'),
        })
    
    return JsonResponse({'data': data})


@csrf_exempt
@require_http_methods(["POST"])
def api_test_create(request):
    data = json.loads(request.body)
    
    test = Test.objects.create(
        title=data['title'],
        description=data.get('description', ''),
        category=data['category'],
        test_type=data['test_type'],
        difficulty=data.get('difficulty', 'medium'),
        duration=data['duration'],
        questions_count=data.get('questions_count', 0),
        test_questions=data.get('questions', []),
        is_active=data.get('is_active', True),
    )
    
    return JsonResponse({'success': True, 'id': test.id})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_test_detail(request, test_id):
    if request.method == "GET":
        test = get_object_or_404(Test, id=test_id)
        return JsonResponse({
            'id': test.id,
            'title': test.title,
            'description': test.description,
            'category': test.category,
            'test_type': test.test_type,
            'difficulty': test.difficulty,
            'duration': test.duration,
            'questions_count': test.questions_count,
            'questions': test.test_questions,
            'is_active': test.is_active,
        })
    
    elif request.method == "POST":
        test = get_object_or_404(Test, id=test_id)
        data = json.loads(request.body)
        
        for field in ['title', 'description', 'category', 'test_type', 'difficulty', 'duration', 'questions_count', 'is_active', 'test_questions']:
            if field in data:
                setattr(test, field, data[field])
            elif field == 'test_questions' and 'questions' in data:
                test.test_questions = data['questions']
        
        test.save()
        return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_test_delete(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test.delete()
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["GET"])
def api_results_list(request):
    user_id = request.GET.get('user_id')
    test_id = request.GET.get('test_id')
    
    results = TestResult.objects.select_related('user', 'test').all()
    
    if user_id:
        results = results.filter(user_id=user_id)
    
    if test_id:
        results = results.filter(test_id=test_id)
    
    results = results.order_by('-completed_at')[:100]
    
    data = [{
        'id': result.id,
        'user_name': f"{result.user.first_name} {result.user.last_name}".strip() or result.user.username,
        'user_email': result.user.email,
        'test_title': result.test.title,
        'test_category': result.test.category,
        'score': float(result.score),
        'band_score': float(result.band_score),
        'time_spent': result.time_spent,
        'completed_at': result.completed_at.strftime('%Y-%m-%d %H:%M'),
    } for result in results]
    
    return JsonResponse({'data': data})


# Payment configuration placeholders
CLICK_API_KEY = "PLACEHOLDER_CLICK_KEY"
PAYME_API_KEY = "PLACEHOLDER_PAYME_KEY"

@login_required
def payment_page(request):
    settings = PricingSettings.get_settings()
    test_id = request.GET.get('test_id')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        post_test_id = request.POST.get('test_id')
        
        # Initialize payment object
        payment = Payment.objects.create(
            user=request.user,
            payment_method=payment_method,
            amount=settings.exam_price,
            status='processing' if float(settings.exam_price) > 0 else 'completed',
            payment_type='exam'
        )

        if payment_method == 'uzcard':
            card_number = request.POST.get('card_number', '').replace(' ', '')
            card_expiry = request.POST.get('card_expiry', '')
            
            if len(card_number) != 16:
                messages.error(request, "Karta raqami noto'g'ri kiritilgan.")
                return render(request, 'main/payment.html', {'settings': settings, 'test_id': test_id})
            
            payment.card_number = card_number[-4:]
            payment.card_expiry = card_expiry
            payment.save()
            
            # Processing Uzcard/Humo simulation
            if float(settings.exam_price) > 0:
                import time
                time.sleep(2)
            
        elif payment_method == 'click':
            # CLICK Integration Placeholder
            # Use CLICK_API_KEY to process payment via API
            # For now, simulate success
            pass
            
        elif payment_method == 'payme':
            # PAYME Integration Placeholder
            # Use PAYME_API_KEY to process payment via API
            # For now, simulate success
            pass
            
        payment.status = 'completed'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Grant premium status to the user
        request.user.subscription = 'premium'
        request.user.save()
        
        messages.success(request, f"✅ To'lovni muvaffaqiyatli amalga oshirdingiz! Endi barcha testlardan foydalanishingiz mumkin.")
        
        # Store test_id in session to be picked up by start_exam
        if post_test_id:
            request.session['pending_test_id'] = post_test_id
        else:
            # If no specific test_id, mark that they paid for a generic/any test attempt
            request.session['has_paid_for_attempt'] = True
        
        return redirect('start_exam')
    
    return render(request, 'main/payment.html', {'settings': settings, 'test_id': test_id})


@staff_member_required(login_url='/django-admin/login/')
def admin_payments(request):
    return render(request, 'admin/payments.html')


@csrf_exempt
@staff_member_required(login_url='/django-admin/login/')
def api_admin_payments(request):
    from decimal import Decimal
    from django.db import models as db_models
    
    payments = Payment.objects.select_related('user').all().order_by('-created_at')
    
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=db_models.Sum('amount')
    )['total'] or Decimal('0')
    
    exam_count = Payment.objects.filter(payment_type='exam', status='completed').count()
    subscription_count = Payment.objects.filter(payment_type='subscription', status='completed').count()
    
    payments_data = []
    for payment in payments:
        payments_data.append({
            'id': payment.id,
            'transaction_id': payment.transaction_id,
            'user_name': payment.user.get_full_name() or payment.user.username,
            'user_email': payment.user.email,
            'payment_type': payment.payment_type,
            'amount': str(payment.amount),
            'payment_method': payment.payment_method,
            'status': payment.status,
            'created_at': payment.created_at.isoformat(),
        })
    
    return JsonResponse({
        'payments': payments_data,
        'total_revenue': float(total_revenue),
        'exam_count': exam_count,
        'subscription_count': subscription_count,
    })


@csrf_exempt
@staff_member_required(login_url='/django-admin/login/')
def api_pricing_settings(request):
    if request.method == 'GET':
        settings = PricingSettings.get_settings()
        return JsonResponse({
            'exam_price': str(settings.exam_price),
            'subscription_price': str(settings.subscription_price),
        })
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        settings = PricingSettings.get_settings()
        settings.exam_price = data.get('exam_price')
        settings.subscription_price = data.get('subscription_price')
        settings.save()
        return JsonResponse({'success': True})


def error_404(request, exception):
    return render(request, '404.html', status=404)


def error_500(request):
    return render(request, '500.html', status=500)
