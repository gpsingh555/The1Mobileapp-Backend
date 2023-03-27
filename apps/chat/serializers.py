from rest_framework import serializers

from apps.chat.models import UserChatHistory, UserAudioVideoCallHistory, ChatGroup
from apps.cms.models import CMS
from utils.exceptions import APIException400


class UserChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChatHistory
        fields = "__all__"


class UserAudioVideoCallHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAudioVideoCallHistory
        fields = "__all__"


class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = "__all__"