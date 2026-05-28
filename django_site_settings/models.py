from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel


class DataType(models.TextChoices):
    STRING = 'string', _('String')
    INTEGER = 'integer', _('Integer')
    FLOAT = 'float', _('Float')
    BOOLEAN = 'boolean', _('Boolean')


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