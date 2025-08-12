from __future__ import annotations

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager with email as unique identifier."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model using email as the USERNAME_FIELD."""

    email = models.EmailField("email address", unique=True, db_comment="邮箱地址（唯一）")
    first_name = models.CharField(_("名"), max_length=150, blank=True, db_comment="名")
    last_name = models.CharField(_("姓"), max_length=150, blank=True, db_comment="姓")
    is_staff = models.BooleanField(
        _("工作人员状态"),
        default=False,
        help_text=_("指定用户是否可以登录到此管理站点。"),
        db_comment="是否可登录管理站点",
    )
    is_active = models.BooleanField(
        _("激活"),
        default=True,
        help_text=_("指定用户是否应被视为活动状态。取消选择而不是删除账户。"),
        db_comment="是否为活动用户",
    )
    date_joined = models.DateTimeField(_("加入时间"), default=timezone.now, db_comment="加入时间")

    email_verified = models.BooleanField(
        _("邮箱已验证"), default=False, db_comment="邮箱是否已验证"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("用户")
        verbose_name_plural = _("用户")
        db_table_comment = "用户表"

    def __str__(self) -> str:  # pragma: no cover - readable repr
        return self.email

    def get_full_name(self) -> str:
        return f"{self.last_name}{self.first_name}".strip() or self.email

    def get_short_name(self) -> str:
        return self.first_name or self.email.split("@")[0]

    def email_user(
        self, subject: str, message: str, from_email: str | None = None, **kwargs
    ) -> None:
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Profile(models.Model):
    """Profile attached to User via OneToOne."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        db_comment="关联用户",
    )
    nickname = models.CharField(_("昵称"), max_length=50, blank=True, db_comment="昵称")
    avatar = models.ImageField(
        _("头像"), upload_to="avatars/", blank=True, null=True, db_comment="头像"
    )
    bio = models.TextField(_("简介"), blank=True, db_comment="个人简介")
    website = models.URLField(_("个人网址"), blank=True, db_comment="个人网站")

    class Meta:
        verbose_name = _("个人资料")
        verbose_name_plural = _("个人资料")
        db_table_comment = "用户个人资料"

    def __str__(self) -> str:  # pragma: no cover
        return f"Profile<{self.user.email}>"
