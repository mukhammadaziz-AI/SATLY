from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import random


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        if not user.username:
            user.username = user.email.split('@')[0] + str(random.randint(100, 999))
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        pass
    
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        if not user.username:
            email = data.get('email', '')
            user.username = email.split('@')[0] + str(random.randint(100, 999))
        
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        
        if not user.username:
            user.username = user.email.split('@')[0] + str(random.randint(100, 999))
        
        user.save()
        sociallogin.save(request)
        return user
