from rest_framework import serializers

from apps.issues.models import UserQuery
from utils.utils import get_unique_ticket_id


class QueryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = ("status", 'subject', 'desc')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        request = self.context.get("request")
        return UserQuery.objects.create(user=request.user, ticket_id=
        get_unique_ticket_id(), **validated_data)


class QueryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = ("id", "ticket_id", "status", 'subject', "comment", 'desc', "created_at")


class QueryPartialListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = {
            "full_name": obj.user.first_name + " " + obj.user.last_name,
            "mobile": obj.user.username,
            "email": obj.user.email
        }
        return user

    class Meta:
        model = UserQuery
        fields = ("id", "ticket_id", "status", "subject", "comment", "created_at", "user", "desc", "user")


class QueryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = ("status",)


class QueryCommentUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField()
    id = serializers.IntegerField()

    class Meta:
        model = UserQuery
        fields = ("comment", "id")
