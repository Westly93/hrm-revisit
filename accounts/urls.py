from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django_email_verification import urls as email_urls
from django.urls import path, reverse_lazy, include

from .views import (
    dashboard,
    add_reference,
    edit_reference,
    add_contact,
    NewPasswordChangeView,
    UserProfileView,
    UserRegisterView,
    password_change_done,
    activate, activate_account,
)

app_name = "accounts"
urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path('inactive/', activate_account, name="inactive"),
    path('email/', include(email_urls)),
    path(
        "login/", LoginView.as_view(template_name="accounts/login.html"), name="login"
    ),
    path("register/", UserRegisterView.as_view(), name="register"),

    path(
        "logout/",
        LogoutView.as_view(template_name="accounts/logout.html"),
        name="logout",
    ),
    path("profile/update/", UserProfileView.as_view(), name="profile-update"),
    path("activate/<uidb64>/<token>", activate, name="activate"),
    # password reset
    path("password_change/", NewPasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", password_change_done,
         name="password_change_done"),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name='accounts/password_reset_email.html',
            success_url=reverse_lazy('accounts:password_reset_done')),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy('accounts:password_reset_complete')
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("references/", add_reference, name="add_reference"),
    path("references/<int:pk>/edit", edit_reference, name="edit_reference"),
    path("contacts/", add_contact, name="add_contact"),
]
