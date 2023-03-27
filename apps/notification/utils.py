from django.conf import settings
from pyfcm import FCMNotification


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

