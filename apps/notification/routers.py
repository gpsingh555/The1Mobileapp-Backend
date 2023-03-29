from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.notification.views import UserNotificationSettingAPIView, NotificationViewSet

router = SimpleRouter()

router.register(r'', NotificationViewSet, basename='notification')


urlpatterns = [
    path('user/setting', UserNotificationSettingAPIView.as_view(), name='user-notification-setting'),
    # path('users', UserListViewSet.as_view(), name='users'),

]

urlpatterns += router.urls
