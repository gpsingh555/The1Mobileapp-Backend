from django.contrib.auth.models import User
from django.db import models

from apps.orders.models import SERVICE_CHOICES

NORMAL_NOTIFICATION, BROADCAST_NOTIFICATION = "1", "2"

NOTIFICATION_CHOICES = (
    (NORMAL_NOTIFICATION, "ORDER_SERVICE_NOTIFICATION"),
    (BROADCAST_NOTIFICATION, "BROADCAST_NOTIFICATION")
)


class UserNotificationSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    account_re_notification = models.BooleanField(default=True)
    order_re_notification = models.BooleanField(default=True)
    updates = models.BooleanField(default=True)
    new_user_reg = models.BooleanField(default=True)
    order_failure = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notification_setting'

    def __str__(self):
        return str(self.id)


class Notification(models.Model):
    users = models.ManyToManyField(User)
    title = models.CharField(max_length=500)
    desc = models.TextField()
    schedule_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User,
                                   null=True, on_delete=models.SET_NULL,
                                   related_name="notification_created_by")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'

    def __str__(self):
        return str(self.id)


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_notification")
    # if it is coming from admin_notification
    admin_notification = models.ForeignKey(Notification, null=True, on_delete=models.SET_NULL)

    # if it is general notification
    title = models.CharField(max_length=500)
    desc = models.TextField()
    order_service_type = models.CharField(max_length=100, blank=True, null=True, choices=SERVICE_CHOICES)
    notification_type = models.CharField(max_length=100, choices=NOTIFICATION_CHOICES)

    is_send = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    seen_at = models.DateTimeField(null=True, blank=True)
    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notification'

    def __str__(self):
        return str(self.id)
