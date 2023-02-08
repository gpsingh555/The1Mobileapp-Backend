from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.notification.models import UserNotificationSetting
from apps.notification.serializers import NotificationSerializer, NotificationUpdateSerializer
from utils.exceptions import APIException404
from utils.response import response



# Create your views here.


class UserNotificationSettingAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """

    method for handle events on stripe
    """

    def get(self, request, *args, **kwargs):
        qs = UserNotificationSetting.objects.filter(user=request.user)
        if qs.exists():
            data = NotificationSerializer(qs[0]).data
        else:
            data = {}

        return response(status_code=200, data=data, message='success')

    def put(self, request, *args, **kwargs):
        data = request.data
        object = UserNotificationSetting.objects.filter(id=data.get("id")).first()
        print(object)
        if not object:
            raise APIException404({"error": "resource not found"})

        serializer = NotificationUpdateSerializer(object, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully updated')
