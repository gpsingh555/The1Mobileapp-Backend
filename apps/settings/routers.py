from django.urls import path

from rest_framework.routers import SimpleRouter

from apps.settings.views import UserProfileSettingAPIView, EmailUpdateAPIView, LocationUpdateAPIView, \
    ChatSettingUpdateAPIView, UpdateProfileImageAPIView

router = SimpleRouter()


urlpatterns = [
    path('user-profile', UserProfileSettingAPIView.as_view(), name='user-settings'),
    path('update-email', EmailUpdateAPIView.as_view(), name='update-email'),
    path('location', LocationUpdateAPIView.as_view(), name='update-location'),
    path('chat-setting', ChatSettingUpdateAPIView.as_view(), name='chat-setting'),
    path('update-profile-pic', UpdateProfileImageAPIView.as_view(), name='change-profile')

]

urlpatterns += router.urls
