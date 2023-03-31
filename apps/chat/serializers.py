from rest_framework import serializers
from django.contrib.auth.models import User

from apps.chat.models import UserChatHistory, UserAudioVideoCallHistory, ChatGroup, MemberInChatGroup
from apps.cms.models import CMS
from utils.exceptions import APIException400


class UserChatHistorySerializer(serializers.ModelSerializer):
    chat_init_user = serializers.CharField(required=True)
    second_user = serializers.CharField(required=True)

    class Meta:
        model = UserChatHistory
        fields = ("second_user", "chat_init_user")

    def validate_chat_init_user(self, val):
        user = User.objects.filter(email=val)
        if not user.exists():
            raise APIException400({
                'error': f'This email does not exists -{val}',
            })
        return user.first()

    def validate_second_user(self, val):
        user = User.objects.filter(email=val)
        if not user.exists():
            raise APIException400({
                'error': f'This email does not exists -{val}',
            })
        return user.first()


class UserAudioVideoCallHistorySerializer(serializers.ModelSerializer):
    sender = serializers.CharField(required=True)
    receivers = serializers.ListField(required=True, allow_empty=False, allow_null=False)

    def validate_sender(self, val):
        user = User.objects.filter(email=val)
        if not user.exists():
            raise APIException400({
                'error': f'This email does not exists -{val}',
            })
        return user.first()

    def validate_receivers(self, vals):
        if not vals:
            raise APIException400({
                'error': f'At least one receivers required',
            })
        users = []
        for val in vals:
            user = User.objects.filter(email=val)
            if not user.exists():
                raise APIException400({
                    'error': f'This email does not exists -{val}',
                })
            users.append(user.first())
        return users

    class Meta:
        model = UserAudioVideoCallHistory
        fields = "__all__"

    # def create(self, validated_data):
    #     print(validated_data)
    #     # members = validated_data.pop('members', [])
    #     receivers = validated_data.pop('receivers', [])
    #
    #     obj = UserAudioVideoCallHistory.objects.create(
    #         sender=validated_data.get("sender"),
    #         start_time=validated_data.get("start_time"),
    #         end_time=validated_data.get("end_time"),
    #         duration=validated_data.get("duration"),
    #         group_id=validated_data.get("group_id"),
    #
    #     )
    #     bulk_obj = []
    #     # print(validated_data)
    #     # for member in members:
    #     #     bulk_obj.append(MemberInChatGroup(
    #     #         chat_group=obj,
    #     #         member=member
    #     #     ))
    #     # MemberInChatGroup.objects.bulk_create(bulk_obj)
    #     obj.receivers.set(receivers)
    #     return obj


class UserChatHistoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChatHistory
        fields = ("id", "chat_init_user", "second_user", "created_at", "is_reported")


class ChatGroupSerializer(serializers.ModelSerializer):
    admin_id = serializers.CharField(required=True)
    members = serializers.ListField(required=True, allow_empty=False, allow_null=False)

    def validate_admin_id(self, val):
        user = User.objects.filter(email=val)
        if not user.exists():
            raise APIException400({
                'error': f'This email does not exists -{val}',
            })
        return user.first()

    def validate_members(self, vals):
        if not vals:
            raise APIException400({
                'error': f'At least one members required',
            })
        users = []
        for val in vals:
            user = User.objects.filter(email=val)
            if not user.exists():
                raise APIException400({
                    'error': f'This email does not exists -{val}',
                })
            users.append(user.first())
        return users

    class Meta:
        model = ChatGroup
        fields = "__all__"

    def create(self, validated_data):
        print(validated_data)
        members = validated_data.pop('members', [])
        admin_id = validated_data.pop('admin_id', None)
        obj = ChatGroup.objects.create(admin_id=admin_id, **validated_data)
        bulk_obj = []
        print(validated_data)
        for member in members:
            bulk_obj.append(MemberInChatGroup(
                chat_group=obj,
                member=member
            ))
        MemberInChatGroup.objects.bulk_create(bulk_obj)
        return obj
