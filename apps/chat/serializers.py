from django.db.models.functions import Concat
from rest_framework import serializers
from django.contrib.auth.models import User

from apps.chat.models import UserChatHistory, UserAudioVideoCallHistory, ChatGroup, MemberInChatGroup, CALL_TYPE
from apps.cms.models import CMS
from utils.exceptions import APIException400
from django.db.models import Value as V


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
    call_type = serializers.ChoiceField(choices=CALL_TYPE)

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

    def validate(self, data):
        if not data.get("duration") and not (data.get("start_time") and data.get("start_time")):
            raise APIException400({
                'error': "Please provide Start time and end time or call duration",
            })
        return data

    class Meta:
        model = UserAudioVideoCallHistory
        fields = "__all__"


class UserChatHistoryDetailSerializer(serializers.ModelSerializer):
    chat_init_user = serializers.SerializerMethodField()
    second_user = serializers.SerializerMethodField()

    def get_chat_init_user(self, obj):
        return {"full_name": obj.chat_init_user.first_name + " " + obj.chat_init_user.last_name,
                "mobile": obj.chat_init_user.username}

    def get_second_user(self, obj):
        return obj.second_user.first_name + " " + obj.second_user.last_name

    class Meta:
        model = UserChatHistory
        fields = ("id", "chat_init_user", "second_user", "is_active", "is_reported", "created_at")


class UserGroupHistoryDetailSerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    def get_admin(self, obj):
        return {"full_name": obj.admin_id.first_name + " " + obj.admin_id.last_name,
                "mobile": obj.admin_id.username}

    def get_members(self, obj):
        return obj.members.all().annotate(
            full_name=Concat('first_name', V(' '), 'last_name')).values("id", "full_name")

    class Meta:
        model = ChatGroup
        fields = ("id", "name", "admin", "members", "is_reported", "is_active", "group_id", "created_at")


class UserAudioVideoHistoryDetailSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receivers = serializers.SerializerMethodField()

    def get_sender(self, obj):
        return {"full_name": obj.sender.first_name + " " + obj.sender.last_name,
                "mobile": obj.sender.username}

    def get_receivers(self, obj):
        return obj.receivers.all().annotate(
            full_name=Concat('first_name', V(' '), 'last_name')).values("id", "full_name")

    class Meta:
        model = UserAudioVideoCallHistory
        fields = ("id", "sender", "receivers", "start_time",
                  "end_time", "duration", "group_id", "created_date", "call_type")


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
