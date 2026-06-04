from django.conf import settings
from django.core.cache import caches
from .models import AppSetting
from .models import SiteAnnouncement

CACHE_PREFIX = "django_site_setting:"
SITE_SETTINGS_CACHE_TIMEOUT = getattr(settings, "SITE_SETTINGS_CACHE_TIMEOUT", 86400 * 7)
SITE_ANNOUNCEMENT_CACHE_TIMEOUT = getattr(settings, "SITE_ANNOUNCEMENT_CACHE_TIMEOUT", 3600)

CACHE_ALIAS = getattr(settings, "SITE_SETTINGS_CACHE_ALIAS", "default")


def get_cache_backend():
    return caches[CACHE_ALIAS]


def get_setting(key: str, default=None):
    cache = get_cache_backend()
    cache_key = f"{CACHE_PREFIX}{key}"
    cached_val = cache.get(cache_key)

    if cached_val is not None:
        return cached_val

    try:
        setting = AppSetting.objects.get(key=key)
        val = setting.get_typed_value()
        cache.set(cache_key, val, timeout=SITE_SETTINGS_CACHE_TIMEOUT)
        return val
    except AppSetting.DoesNotExist:
        return default


def get_active_announcements():
    cache = get_cache_backend()
    cache_key = SiteAnnouncement.SITE_ANNOUNCEMENT_CACHE_KEY
    announcements = cache.get(cache_key)

    if announcements is None:
        announcements = list(SiteAnnouncement.objects.active())
        cache.set(cache_key, announcements, timeout=SITE_ANNOUNCEMENT_CACHE_TIMEOUT)

    return announcements
