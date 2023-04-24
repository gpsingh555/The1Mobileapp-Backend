from rest_framework import serializers

from account.models import Userprofile, LANGUAGES_CHOICES
from apps.settings.models import ChatSettings, CHAT_BACKUP, FONT_SIZE
from utils.exceptions import APIException400
from rest_framework.authtoken.admin import User


class UserProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    dob = serializers.DateField()
    user_bio = serializers.CharField(max_length=500)

    class Meta:
        fields = ("first_name", "first_name", "dob", "user_bio",)

    def update(self, instance, validated_data):
        instance.first_name = validated_data["first_name"]
        instance.last_name = validated_data["last_name"]
        instance.save()
        user_profile = instance.user_profile
        user_profile.dob = validated_data["dob"]
        user_profile.user_bio = validated_data["user_bio"]
        user_profile.save()
        return instance


class UpdateEmailSerializer(serializers.ModelSerializer):
    curr_email = serializers.EmailField()
    new_email = serializers.EmailField()
    conf_email = serializers.EmailField()

    class Meta:
        model = User
        fields = ("curr_email", "new_email", "conf_email",)

    def validate(self, attrs):
        if attrs["new_email"] != attrs["conf_email"]:
            raise APIException400({"error": "New Email and Confirm email is not matching"})

        if self.instance.email != attrs["curr_email"]:
            raise APIException400({"error": "Current email is incorrect"})

        if User.objects.filter(email=attrs["new_email"]).exists():
            raise APIException400({"error": f"User with this email {self.instance.email} is already exists"})

        return attrs

    def update(self, instance, validated_data):
        instance.email = validated_data["new_email"]
        instance.save()
        return instance


class LocationUpdateSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(choices=LANGUAGES_CHOICES)

    class Meta:
        model = Userprofile
        fields = ("language", "country",)


class ChatSettingSerializer(serializers.ModelSerializer):
    chat_backup = serializers.ChoiceField(choices=CHAT_BACKUP)
    font_size = serializers.ChoiceField(choices=FONT_SIZE)
    media_visibility = serializers.BooleanField()

    class Meta:
        model = ChatSettings
        fields = ("chat_backup", "font_size", "media_visibility")

    def create(self, validated_data):
        obj = ChatSettings.objects.create(
            user=self.context["request"].user,
            **validated_data
        )
        return obj

    def update(self, instance, validated_data):
        instance.chat_backup = validated_data["chat_backup"]
        instance.font_size = validated_data["font_size"]
        instance.media_visibility = validated_data["media_visibility"]
        instance.save()
        return instance