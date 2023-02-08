from django.conf import settings
from rest_framework import serializers

from apps.orders.models import AvailableRecharge, Orders, ETISALAT_SERVICES
from utils.exceptions import APIException400


class PlaceOrderSerializer(serializers.Serializer):
    """
    Serializer to create order.
    """
    payment_intent_id = serializers.CharField()

    class Meta:
        fields = ('payment_intent_id',)


class AvailableRechargeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableRecharge
        fields = "__all__"


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ("created_at", "status", "amount",
                  "service_type", "order_id")


class OrderDetailSerializer(serializers.ModelSerializer):
    transaction_details = serializers.SerializerMethodField()

    def get_transaction_details(self, obj):
        payment_obj = obj.payment.first()
        if payment_obj:
            return {"transaction_id": payment_obj.transaction_id,
                    "payment_method": payment_obj.payment_method, "payment_provider": payment_obj.payment_provider}
        return None

    class Meta:
        model = Orders
        fields = ("created_at", "status", "amount", "recharge_number",
                  "service_type", "recharge_type", "transaction_details", "order_id")


class OrderListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ("id", "created_at", "status", "amount",
                  "service_type", "order_id", "user", "recharge_number")


class OrderDetailViewSerializer(serializers.ModelSerializer):
    transaction_details = serializers.SerializerMethodField()

    def get_transaction_details(self, obj):
        payment_obj = obj.payment.first()
        if payment_obj:
            return {"transaction_id": payment_obj.transaction_id,
                    "payment_method": payment_obj.payment_method,
                    "payment_provider": payment_obj.payment_provider}
        return None

    class Meta:
        model = Orders
        fields = ("created_at", "status", "amount",
                  "service_type", "order_id", "user", "recharge_number", "recharge_type",
                  "transaction_details")


class ValidateNOLSerializer(serializers.Serializer):
    card_number = serializers.CharField()

    class Meta:
        fields = ("card_number",)


class ValidateSalikDirectSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    account_pin = serializers.CharField()

    class Meta:
        fields = ("account_number", "account_pin",)


class ValidateHafilatSerializer(serializers.Serializer):
    card_number = serializers.CharField()

    class Meta:
        fields = ("card_number",)

class ValidateEtisalatSerializer(serializers.Serializer):
    """
    GSM for postpaid GSM, DEL for Landline telephones, DAILUP for Internet Dialup, BROADBAND for AlShamil,
    EViSION for eVision, ELIFE for eLife, WaselRecharge for Wasel recharge.
    """
    account_number = serializers.CharField()
    service_offered = serializers.ChoiceField(choices=ETISALAT_SERVICES)

    class Meta:
        fields = ("account_number", "service_offered",)
