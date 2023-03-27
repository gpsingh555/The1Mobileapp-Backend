from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from account.models import Userprofile
from apps.notification.models import UserNotificationSetting, Notification
from apps.notification.serializers import NotificationSerializer, NotificationUpdateSerializer, \
    NotificationListSerializer, NotificationCreateSerializer
from apps.notification.utils import Firebase
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


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-created_at',)

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return super(NotificationViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        qs = Notification.objects.all()
        response_data = self.serializer_class(qs, many=True).data
        return response(data=response_data, message="success")

    def create(self, request, *args, **kwargs):
        serializer = NotificationCreateSerializer(data=request.data,  # or request.data
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # get device ids
        tokens = Userprofile.objects.filter(id__in=request.data["users"],
                                            device_token__isnull=False).values_list(
            "device_token", flat=True)

        # send notification
        if tokens:
            Firebase().send_notification(list(tokens), request.data)
        return response(message="successfully created", status_code=201)
