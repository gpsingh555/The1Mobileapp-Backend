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
        fields = ("ticket_id", "status", 'subject', 'desc', "created_at")


class QueryPartialListSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
    class Meta:
        model = UserQuery
        fields = ("ticket_id", "status", "subject", "created_at", "user", "desc", "user_name")


class QueryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = ("status",)