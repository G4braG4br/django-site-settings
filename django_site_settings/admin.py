from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Settings, AppSetting


class AppSettingInline(admin.TabularInline):
    model = AppSetting
    extra = 0
    fields = ('key', 'description', 'data_type', 'value')


@admin.register(Settings)
class SettingsAdmin(SingletonModelAdmin):
    inlines = [AppSettingInline]