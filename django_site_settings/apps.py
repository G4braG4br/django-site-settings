from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteSettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_site_settings'
    verbose_name = _("Site Settings Engine")

    def ready(self):
        import django_site_settings.signals