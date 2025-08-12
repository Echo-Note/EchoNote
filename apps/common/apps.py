from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommonConfig(AppConfig):
    """Common app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    verbose_name = _("通用模块")
