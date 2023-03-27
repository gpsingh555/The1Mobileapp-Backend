from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.chat.serializers import UserChatHistorySerializer, UserAudioVideoCallHistorySerializer, ChatGroupSerializer
from apps.cms.serializers import CMSCreateSerializer
from utils.response import response


class UserChatHistoryAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    """

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserChatHistorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully Created')


class UserAudioVideoCallHistoryAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    """
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserAudioVideoCallHistorySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully Created')


class ChatGroupAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    """
    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = ChatGroupSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully Created')
