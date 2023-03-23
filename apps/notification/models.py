from django.contrib.auth.models import User
from django.db import models


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
    created_at = models.DateTimeField(auto_now=True)
    schedule_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User,null=True, on_delete=models.SET_NULL, related_name="notification_created_by")

    class Meta:
        db_table = 'notification'

    def __str__(self):
        return str(self.id)
