from rest_framework import serializers

from apps.cms.models import CMS
from apps.notification.models import UserNotificationSetting
from utils.exceptions import APIException400


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSetting
        fields = "__all__"


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationSetting
        fields = ("id", "account_re_notification", "order_re_notification", "updates", "new_user_reg",
                  "order_failure")
