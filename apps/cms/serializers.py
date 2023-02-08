from rest_framework import serializers

from apps.cms.models import CMS
from utils.exceptions import APIException400


class CMSListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMS
        fields = "__all__"


class CMSCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        policy_type = attrs["policy_type"]
        cms_type = attrs["cms_type"]
        if cms_type == CMS.POLICIES and not policy_type:
            raise APIException400({
                "error": "policy_type is required for cms_type 2"
            })
        if cms_type != CMS.POLICIES:
            attrs["policy_type"] = ''
        return attrs

    class Meta:
        model = CMS
        fields = ("heading", "description", "cms_type", "policy_type")


class CMSUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMS
        fields = ("id", "heading", "description")
