from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    """Account app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.account"
    verbose_name = _("账号管理")

    def ready(self) -> None:  # pragma: no cover
        # Import signals
        from . import signals  # noqa: F401

        return super().ready()
