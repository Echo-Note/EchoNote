from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.urls import path

from .views import ProfileView, SignUpView, VerifyEmailView

app_name = "account"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify/<uidb64>/<token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="account/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Password change (requires login)
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(template_name="account/password_change.html"),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="account/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # Password reset (via email)
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="account/password_reset.html",
            email_template_name="account/password_reset_email.txt",
            subject_template_name="account/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="account/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="account/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="account/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
