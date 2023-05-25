from django.contrib import admin

from apps.notification.models import UserNotificationSetting, Notification, UserNotification

# Register your models here.
admin.site.register(UserNotificationSetting)
admin.site.register(Notification)
admin.site.register(UserNotification)


# Register your models here.
