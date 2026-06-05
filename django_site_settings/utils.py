from typing import Any, List, Optional
from django.conf import settings
from django.core.cache import caches
from .models import AppSetting, SiteAnnouncement
from django.core.cache.backends.base import BaseCache

CACHE_PREFIX: str = "django_site_setting:"


def get_cache_backend() -> BaseCache:
    cache_alias: str = getattr(settings, "SITE_SETTINGS_CACHE_ALIAS", "default")
    return caches[cache_alias]


def get_setting(key: str, default: Any = None) -> Any:
    cache: BaseCache = get_cache_backend()
    cache_key: str = f"{CACHE_PREFIX}{key}"
    cached_val: Optional[Any] = cache.get(cache_key)

    if cached_val is not None:
        return cached_val

    try:
        setting: AppSetting = AppSetting.objects.get(key=key)
    except AppSetting.DoesNotExist:
        return default

    try:
        val: Any = setting.get_typed_value()
        timeout: int = getattr(settings, "SITE_SETTINGS_CACHE_TIMEOUT", 86400 * 7)
        cache.set(cache_key, val, timeout=timeout)
        return val
    except (ValueError, TypeError):
        return default


def get_active_announcements() -> List[SiteAnnouncement]:
    cache: BaseCache = get_cache_backend()
    cache_key: str = SiteAnnouncement.SITE_ANNOUNCEMENT_CACHE_KEY
    announcements: Optional[List[SiteAnnouncement]] = cache.get(cache_key)

    if announcements is None:
        announcements = list(SiteAnnouncement.objects.active())
        timeout: int = getattr(settings, "SITE_ANNOUNCEMENT_CACHE_TIMEOUT", 3600)
        cache.set(cache_key, announcements, timeout=timeout)

    return announcements
