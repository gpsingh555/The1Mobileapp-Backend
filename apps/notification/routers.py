from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.notification.views import UserNotificationSettingAPIView

router = SimpleRouter()

urlpatterns = [
    path('user/setting', UserNotificationSettingAPIView.as_view(), name='notification'),


]

urlpatterns += router.urls


