"""博客表单定义。

包含评论提交表单 CommentForm，带有登录态感知的字段校验逻辑。
"""

from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from .models import Comment


class CommentForm(forms.ModelForm):
    """评论表单。

    - 已登录用户无需填写昵称与邮箱；
    - 未登录用户必须填写昵称与邮箱；
    """

    user: AbstractBaseUser | None

    class Meta:
        model = Comment
        fields = ["content", "nickname", "email"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": _("说点什么…")}),
        }

    def __init__(self, *args: Any, user: AbstractBaseUser | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user = user
        if user and getattr(user, "is_authenticated", False):
            # 已登录：昵称与邮箱可选
            self.fields["nickname"].required = False
            self.fields["email"].required = False
        else:
            # 未登录：昵称与邮箱必填
            self.fields["nickname"].required = True
            self.fields["email"].required = True

    def clean(self) -> dict[str, Any]:  # type: ignore[override]
        cleaned = super().clean()
        if not self.user or not getattr(self.user, "is_authenticated", False):
            if not cleaned.get("nickname") or not cleaned.get("email"):
                raise forms.ValidationError(_("未登录用户需要提供昵称和邮箱"))
        return cleaned
