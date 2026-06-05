from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel
from django.core.cache import cache
from django.utils import timezone
from django.contrib.auth.models import Group as DjangoGroup
from django_site_settings.fields import SanitizedHTMLField


class DataType(models.TextChoices):
    STRING = "string", _("String")
    INTEGER = "integer", _("Integer")
    FLOAT = "float", _("Float")
    BOOLEAN = "boolean", _("Boolean")


class LevelChoices(models.TextChoices):
    INFO = "info", _("Information")
    WARNING = "warning", _("Warning")
    DANGER = "danger", _("Critical Alert")


class Settings(SingletonModel):
    class Meta:
        verbose_name = _("Global Configuration")
        verbose_name_plural = _("Global Configurations")

    def __str__(self):
        return str(_("Global Configuration"))


class AppSetting(models.Model):
    settings = models.ForeignKey(
        Settings,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Configuration Base")
    )
    key = models.CharField(_("Key"), max_length=100, unique=True)
    description = models.CharField(_("Description"), max_length=255, blank=True)
    data_type = models.CharField(
        _("Data Type"),
        max_length=20,
        choices=DataType.choices,
        default=DataType.STRING
    )
    value = models.TextField(_("Value"), blank=True)

    class Meta:
        verbose_name = _("Setting Item")
        verbose_name_plural = _("Setting Items")
        ordering = ['key']

    def __str__(self):
        return f"{self.key} ({self.get_data_type_display()})"

    def get_typed_value(self):
        val = self.value
        if self.data_type == DataType.INTEGER:
            return int(val)
        if self.data_type == DataType.FLOAT:
            return float(val)
        if self.data_type == DataType.BOOLEAN:
            return val.strip().lower() in ('true', '1', 'yes', 'on', 'y', 'да')
        return val

    def clean(self):
        super().clean()
        if self.value:
            try:
                self.get_typed_value()
            except (ValueError, TypeError):
                raise ValidationError({
                    'value': _("The entered value does not match the selected data type.")
                })


class AnnouncementQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            is_active=True,
            start_at__lte=now,
            end_at__gte=now
        ).order_by('-priority', '-created_at')


class SiteAnnouncement(models.Model):
    SITE_ANNOUNCEMENT_CACHE_KEY = "active_site_announcement"
    title = models.CharField(
        max_length=255,
        help_text=_("Internal title used only within the Django Admin panel.")
    )
    text = SanitizedHTMLField(
        help_text=_("The announcement message body. Supports plain text or raw HTML raw tags.")
    )
    level = models.CharField(
        max_length=10,
        choices=LevelChoices.choices,
        default=LevelChoices.INFO,
        help_text=_("The visual urgency level of the banner, mapping to bootstrap/tailwind alert classes.")
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Global visibility toggle for this specific announcement.")
    )
    start_at = models.DateTimeField(
        default=timezone.now,
        help_text=_("The exact date and time when the banner should start displaying.")
    )
    end_at = models.DateTimeField(
        help_text=_("The exact date and time when the banner should be automatically hidden.")
    )

    priority = models.IntegerField(
        default=0,
        help_text=_(
            "If multiple announcements are active simultaneously, the one with the highest priority displays first."
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        db_table = "site_announcements"
        verbose_name = "Site Announcement"
        verbose_name_plural = "Site Announcements"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete("active_site_announcement")

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        cache.delete("active_site_announcement")

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "level": self.level,
            "updated_at": self.updated_at.timestamp(),
        }


class SettingAccessGroup(models.Model):
    name = models.CharField(_("Group Name"), max_length=100, unique=True)

    django_groups = models.ManyToManyField(
        DjangoGroup,
        through='GroupDjangoGroupRelation',
        related_name='setting_access_groups',
        related_query_name='setting_access_group',
        verbose_name=_("Django Groups"),
        blank=True,
        null=True,
    )
    setting_items = models.ManyToManyField(
        'AppSetting',
        through='GroupSettingItemRelation',
        related_name='setting_access_groups',
        related_query_name='setting_access_group',
        verbose_name=_("Setting Items"),
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "setting_access_groups"
        verbose_name = _("Setting Access Group")
        verbose_name_plural = _("Setting Access Groups")

    def __str__(self):
        return self.name


class GroupDjangoGroupRelation(models.Model):
    access_group = models.ForeignKey(
        SettingAccessGroup,
        on_delete=models.CASCADE,
        related_name='django_group_relations',
        related_query_name='django_group_relation',
    )
    django_group = models.ForeignKey(
        DjangoGroup,
        on_delete=models.CASCADE,
        related_name='django_group_relations',
        related_query_name='django_group_relation',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "setting_django_group_relation"
        unique_together = ('access_group', 'django_group')
        verbose_name = _("Setting django group relations")
        verbose_name_plural = _("Setting django group relation")


class GroupSettingItemRelation(models.Model):
    access_group = models.ForeignKey(
        SettingAccessGroup,
        on_delete=models.CASCADE,
        related_name='setting_item_relations',
        related_query_name='setting_item_relation',
    )
    setting_item = models.ForeignKey(
        'AppSetting',
        on_delete=models.CASCADE,
        related_name='setting_item_relations',
        related_query_name='setting_item_relation',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "setting_group_item_relations"
        unique_together = ('access_group', 'setting_item')
        verbose_name = _("Setting group item relations")
        verbose_name_plural = _("Setting group item relation")