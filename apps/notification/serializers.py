import datetime

from django.db.models.functions import Concat
from rest_framework import serializers

from apps.cms.models import CMS
from apps.notification.models import UserNotificationSetting, Notification, NORMAL_NOTIFICATION, UserNotification
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
        fields = ("users", "title", "desc", "created_at", "id")


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("users", "title", "desc")

    def create(self, validated_data):
        obj = Notification.objects.create(title=validated_data["title"],
                                          desc=validated_data["desc"])
        obj.users.set(validated_data["users"])
        notification_objs = []
        for u in validated_data["users"]:
            notification_objs.append(UserNotification(
                user=u,
                admin_notification=obj,
                title=validated_data["title"],
                desc=validated_data["desc"],
                notification_type=NORMAL_NOTIFICATION,
                sent_at=datetime.datetime.now()
            ))
        UserNotification.objects.bulk_create(notification_objs)
        return obj


class UserListNotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    desc = serializers.SerializerMethodField()

    def get_title(self, obj):
        if obj.notification_type == NORMAL_NOTIFICATION:
            return obj.title
        return obj.admin_notification.title

    def get_desc(self, obj):
        if obj.notification_type == NORMAL_NOTIFICATION:
            return obj.desc
        return obj.admin_notification.desc

    class Meta:
        model = UserNotification
        fields = ("id", "title", "desc", "order_service_type", "sent_at")


