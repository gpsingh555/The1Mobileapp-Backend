from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView

from apps.settings.models import ChatSettings
from apps.settings.serializers import UserProfileSerializer, UpdateEmailSerializer, LocationUpdateSerializer, \
    ChatSettingSerializer
from apps.settings.utils import UserSetting
from utils.response import response


class UserProfileSettingAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = UserSetting().user_profile(request.user)
        return response(message="success", data=data)

    def put(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(message="updated successfully")


class EmailUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        serializer = UpdateEmailSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(message="updated successfully")


class LocationUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        serializer = LocationUpdateSerializer(request.user.user_profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(message="updated successfully")


class ChatSettingUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        qs = ChatSettings.objects.filter(user=request.user)
        if qs.exists():
            serializer = ChatSettingSerializer(
                qs.first(),
                data=request.data,
                context={"request": self.request}
            )
        else:
            serializer = ChatSettingSerializer(
                data=request.data,
                context={"request": self.request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(message="updated successfully")


class UpdateProfileImageAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        user_profile = request.user.user_profile
        user_profile.image = request.data["image"]
        user_profile.save()
        return response(message="updated successfully")