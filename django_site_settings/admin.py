from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Settings, AppSetting, SiteAnnouncement, SettingAccessGroup, GroupDjangoGroupRelation, GroupSettingItemRelation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class GroupDjangoGroupInline(admin.TabularInline):
    model = GroupDjangoGroupRelation
    extra = 1


class GroupSettingItemInline(admin.TabularInline):
    model = GroupSettingItemRelation
    extra = 1


class AppSettingInline(admin.TabularInline):
    model = AppSetting
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class FormsetWithRequest(formset):
            def __init__(self, *args, **kwargs):
                self.request = request
                super().__init__(*args, **kwargs)

                if request.user.is_superuser:
                    return

                user_groups = request.user.groups.all()

                self.allowed_settings = AppSetting.objects.filter(
                    setting_access_group__django_groups__in=user_groups
                ).distinct()

                self.queryset = self.queryset.filter(id__in=self.allowed_settings)

            def clean(self):
                super().clean()

                if request.user.is_superuser:
                    return

                allowed_ids = set(self.allowed_settings.values_list('id', flat=True))

                for form in self.forms:
                    if not form.cleaned_data or form in self.deleted_forms:
                        continue

                    instance = form.instance

                    if instance.pk and instance.pk not in allowed_ids:
                        raise ValidationError(
                            _("You do not have permission to modify the setting: %(key)s"),
                            params={'key': instance.key},
                        )

        return FormsetWithRequest


@admin.register(Settings)
class SettingsAdmin(SingletonModelAdmin):
    inlines = [AppSettingInline]


@admin.register(SiteAnnouncement)
class SiteAnnouncementAdmin(admin.ModelAdmin):
    pass


@admin.register(SettingAccessGroup)
class SettingAccessGroupAdmin(admin.ModelAdmin):
    inlines = [GroupDjangoGroupInline, GroupSettingItemInline]
