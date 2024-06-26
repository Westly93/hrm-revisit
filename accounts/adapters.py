from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_active = True
        if sociallogin.account.provider == 'google' and user.email.endswith('@staff.msu.ac.zw'):
            user.is_staff = True
        user.save()
        return user
