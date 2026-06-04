from django import template
from django_site_settings.utils import get_setting, get_active_announcements

register = template.Library()


@register.simple_tag
def site_setting(key, default=None):
    return get_setting(key, default=default)


@register.simple_tag
def get_site_announcements():
    return get_active_announcements()
