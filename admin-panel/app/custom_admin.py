from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME

class SatlyAdminSite(AdminSite):
    site_header = "SATLY Administration"
    site_title = "SATLY Admin"
    index_title = "Welcome to SATLY Admin"
    login_template = 'registration/login.html'
    
    def login(self, request, extra_context=None):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('/admin-panel/')
        return super().login(request, extra_context)
    
    def index(self, request, extra_context=None):
        return redirect('/admin-panel/')

satly_admin_site = SatlyAdminSite(name='satly_admin')
