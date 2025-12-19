from .custom_admin import satly_admin_site

def admin_models(request):
    if request.user.is_authenticated and request.user.is_staff:
        app_list = satly_admin_site.get_app_list(request)
        return {'admin_app_list': app_list}
    return {'admin_app_list': []}
