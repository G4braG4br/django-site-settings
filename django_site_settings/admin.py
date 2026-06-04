from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Settings, AppSetting, SiteAnnouncement, SettingAccessGroup, GroupDjangoGroupRelation, GroupSettingItemRelation


class GroupDjangoGroupInline(admin.TabularInline):
    model = GroupDjangoGroupRelation
    extra = 1


class GroupSettingItemInline(admin.TabularInline):
    model = GroupSettingItemRelation
    extra = 1


class AppSettingInline(admin.TabularInline):
    model = AppSetting
    extra = 0
    fields = ('key', 'description', 'data_type', 'value')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class FormsetWithRequest(formset):
            def __init__(self, *args, **kwargs):
                self.request = request
                super().__init__(*args, **kwargs)

                if request.user.is_superuser:
                    return

                user_groups = request.user.groups.all()

                allowed_settings = AppSetting.objects.filter(
                    setting_access_group__django_groups__in=user_groups
                ).distinct()

                self.queryset = self.queryset.filter(id__in=allowed_settings)

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
