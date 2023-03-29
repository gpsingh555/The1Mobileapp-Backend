from django.urls import path

from rest_framework.routers import SimpleRouter

from apps.chat.views import UserChatHistoryAPIView, UserAudioVideoCallHistoryAPIView, ChatGroupAPIView
from apps.issues.views import QueryViewSet

router = SimpleRouter()

# router.register(r'chat', ChatViewSet, basename='chat')


urlpatterns = [

    path('chat-history', UserChatHistoryAPIView.as_view(), name='user-chat-history'),
    path('audio-video-history', UserAudioVideoCallHistoryAPIView.as_view(), name='audio-video-call'),
    path('group-chat-history', ChatGroupAPIView.as_view(), name='chat-group'),

    # Admin panel apis
    # path('', ChatHistoryAPIView.as_view(), name=""),

]

urlpatterns += router.urls