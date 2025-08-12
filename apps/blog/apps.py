from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlogConfig(AppConfig):
    """Blog app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blog"
    verbose_name = _("博客系统")
