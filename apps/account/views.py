from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, UpdateView

from .forms import ProfileForm, SignUpForm

User = get_user_model()


class SignUpView(FormView):
    template_name = "account/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("account:signup")

    def form_valid(self, form):
        user: User = form.save(commit=False)
        # Require email verification before login
        user.is_active = False
        user.save()
        # Send verification email
        self._send_verification_email(self.request, user)
        messages.success(self.request, _("注册成功，请前往邮箱完成验证。"))
        return super().form_valid(form)

    def _send_verification_email(self, request: HttpRequest, user: User) -> None:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = request.build_absolute_uri(
            reverse("account:verify_email", kwargs={"uidb64": uid, "token": token})
        )
        subject = _("请验证你的邮箱")
        message = _("点击以下链接以激活你的账户：\n{url}").format(url=verify_url)
        user.email_user(subject, message)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "account/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("account:profile")

    def get_object(self, queryset=None):
        return self.request.user.profile


class VerifyEmailView(View):
    def get(self, request: HttpRequest, uidb64: str, token: str) -> HttpResponse:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except Exception:  # pragma: no cover - defensive
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.email_verified = True
            user.is_active = True
            user.save(update_fields=["email_verified", "is_active"])
            messages.success(request, _("邮箱验证成功，现在可以登录了。"))
            return redirect("account:login")

        messages.error(request, _("验证链接无效或已过期。"))
        return redirect("account:signup")
