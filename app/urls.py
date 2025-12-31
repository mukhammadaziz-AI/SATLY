from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quick-register/', views.quick_register, name='quick_register'),
    
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/avatar/', views.update_avatar, name='update_avatar'),
    path('dashboard/progress/', views.user_progress, name='user_progress'),
    path('dashboard/settings/', views.user_settings, name='user_settings'),
    
    path('payment/', views.payment_page, name='payment_page'),
    path('exam/', views.start_exam, name='start_exam'),
    path('exam/result/<int:session_id>/', views.exam_result, name='exam_result'),
    
    path('api/exam/save-answer/', views.api_save_answer, name='api_save_answer'),
    path('api/exam/save-time/', views.api_save_time, name='api_save_time'),
    path('api/exam/finish-section/', views.api_finish_section, name='api_finish_section'),
    path('api/exam/start-math/', views.api_start_math, name='api_start_math'),
    
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.user_management, name='admin_users'),
    path('admin-panel/payments/', views.admin_payments, name='admin_payments'),
    path('admin-panel/tests/', views.test_management, name='admin_tests'),
    path('admin-panel/results/', views.results_page, name='admin_results'),
    path('admin-panel/settings/', views.settings_page, name='admin_settings'),
    
    path('api/dashboard/stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/dashboard/daily-active-users/', views.api_daily_active_users, name='api_daily_active_users'),
    path('api/dashboard/tests-completed/', views.api_tests_completed, name='api_tests_completed'),
    path('api/dashboard/top-band-scores/', views.api_top_band_scores, name='api_top_band_scores'),
    
    path('api/users/', views.api_users_list, name='api_users_list'),
    path('api/users/<int:user_id>/', views.api_user_detail, name='api_user_detail'),
    path('api/users/<int:user_id>/delete/', views.api_user_delete, name='api_user_delete'),
    
    path('api/admin/users/', views.api_admin_users, name='api_admin_users'),
    path('api/admin/users/<int:user_id>/', views.api_admin_user_detail, name='api_admin_user_detail'),
    path('api/admin/users/<int:user_id>/delete/', views.api_admin_user_delete, name='api_admin_user_delete'),
    
    path('api/admin/payments/', views.api_admin_payments, name='api_admin_payments'),
    path('api/admin/pricing-settings/', views.api_pricing_settings, name='api_pricing_settings'),
    
    path('api/pricing/', views.api_pricing, name='api_pricing'),
    
    path('api/tests/', views.api_tests_list, name='api_tests_list'),
    path('api/tests/create/', views.api_test_create, name='api_test_create'),
    path('api/tests/<int:test_id>/', views.api_test_detail, name='api_test_detail'),
    path('api/tests/<int:test_id>/delete/', views.api_test_delete, name='api_test_delete'),
    
    path('api/results/', views.api_results_list, name='api_results_list'),
    
    # Payment webhook endpoints (for Click and Payme callbacks)
    path('api/click/callback/', views.click_callback, name='click_callback'),
    path('api/payme/callback/', views.payme_callback, name='payme_callback'),
]