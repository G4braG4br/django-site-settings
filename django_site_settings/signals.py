from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import AppSetting
from .utils import CACHE_PREFIX


@receiver([post_save, post_delete], sender=AppSetting)
def invalidate_setting_cache(sender, instance, **kwargs):
    cache_key = f"{CACHE_PREFIX}{instance.key}"
    cache.delete(cache_key)
