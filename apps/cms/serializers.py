from rest_framework import serializers

from apps.cms.models import CMS, CMS_TYPE_CHOICES, FAQ
from utils.exceptions import APIException400


class CMSListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMS
        fields = "__all__"


class CMSCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField()
    heading = serializers.CharField(allow_null=True, allow_blank=True)
    cms_type = serializers.ChoiceField(choices=CMS_TYPE_CHOICES)

    def validate(self, attrs):
        cms_type = attrs["cms_type"]
        if cms_type == FAQ and not attrs.get("heading"):
            raise APIException400({
                "error": "heading is required"
            })
        return attrs

    class Meta:
        model = CMS
        fields = ("heading", "description", "cms_type")

    def create(self, validated_data):
        if validated_data["cms_type"] == FAQ:
            obj = CMS.objects.create(
                cms_type=validated_data["cms_type"],
                description=validated_data["description"],
                heading=validated_data["heading"],
            )
        else:
            qs = CMS.objects.filter(cms_type=validated_data["cms_type"])
            if qs.exists():
                obj = qs.first()
                obj.description = validated_data["description"]
                obj.save()
            else:
                obj = CMS.objects.create(
                    cms_type=validated_data["cms_type"],
                    description=validated_data["description"]
                )

        return obj


class CMSUpdateSerializer(serializers.ModelSerializer):
    heading = serializers.CharField()

    class Meta:
        model = CMS
        fields = ("id", "heading", "description")
