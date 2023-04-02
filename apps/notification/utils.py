from django.conf import settings
from pyfcm import FCMNotification

from apps.notification.models import Notification
from apps.notification.serializers import NotificationListSerializer


class Firebase:

    def send_notification(self, registration_ids: list, data: dict):
        print(registration_ids, data)
        push_service = FCMNotification(api_key=settings.FIREBASE_SERVER)
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids,
            message_title=data["title"],
            message_body=data["desc"]
        )
        print(result)


class Notifications:
    def __init__(self, request):
        self.request = request

    def list_all_notification(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}
        qs = Notification.objects.all().order_by("-created_at")
        if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
            qs = qs.filter(
                created_at__date__gte=self.request.GET.get('from_date'),
                created_at__date__lte=self.request.GET.get('to_date')
            )

        data["total_results"] = qs.count()
        qs = qs[offset:limit]
        data["results"] = NotificationListSerializer(qs, many=True).data
        return data
