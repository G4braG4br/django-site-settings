from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AppSetting
from .utils import CACHE_PREFIX, get_cache_backend


@receiver([post_save, post_delete], sender=AppSetting)
def invalidate_setting_cache(sender, instance, **kwargs):
    cache = get_cache_backend()
    cache_key = f"{CACHE_PREFIX}{instance.key}"
    cache.delete(cache_key)
