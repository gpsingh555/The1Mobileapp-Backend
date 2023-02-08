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
