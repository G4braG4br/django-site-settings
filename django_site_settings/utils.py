from django.core.cache import cache
from .models import AppSetting

CACHE_PREFIX = "django_site_setting:"
CACHE_TIMEOUT = 86400 * 7


def get_setting(key: str, default=None):
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
