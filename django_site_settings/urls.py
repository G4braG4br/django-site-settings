from django.urls import path
from .views import ActiveAnnouncementsAPIView

app_name = "django_site_settings"

urlpatterns = [
    path("api/announcements/", ActiveAnnouncementsAPIView.as_view(), name="active_announcements_api"),
]
