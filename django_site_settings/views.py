from django.http import JsonResponse
from django.views import View
from .utils import get_active_announcements


class ActiveAnnouncementsAPIView(View):
    def get(self, request, *args, **kwargs):
        announcements = get_active_announcements()
        data = [item.to_dict() for item in announcements]
        return JsonResponse({"announcements": data}, status=200)
