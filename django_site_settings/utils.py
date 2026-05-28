from django.conf import settings
from django.core.cache import caches
from .models import AppSetting

CACHE_PREFIX = "django_site_setting:"
CACHE_TIMEOUT = getattr(settings, "SITE_SETTINGS_CACHE_TIMEOUT", 86400 * 7)

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
        cache.set(cache_key, val, timeout=CACHE_TIMEOUT)
        return val
    except AppSetting.DoesNotExist:
        return default
