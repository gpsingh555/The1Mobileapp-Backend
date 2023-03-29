from django.db.models.functions import Concat
from rest_framework import serializers

from apps.cms.models import CMS
from apps.notification.models import UserNotificationSetting, Notification
from utils.exceptions import APIException400
from django.db.models import Value as V
from django.contrib.auth.models import User


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSetting
        fields = "__all__"


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSetting
        fields = ("id", "account_re_notification", "order_re_notification", "updates", "new_user_reg",
                  "order_failure")


class NotificationListSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        return obj.users.all().annotate(full_name=Concat('first_name', V(' '), 'last_name')).values("id", "full_name")

    class Meta:
        model = Notification
        fields = ("users", "title", "desc", "created_at")


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("users", "title", "desc")


class UserListNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "user_name", "email")

