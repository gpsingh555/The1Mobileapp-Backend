import asyncio
import datetime

from asgiref.sync import sync_to_async, async_to_sync
from django.conf import settings
from rest_framework import serializers

from apps.orders.api_clients.du_prepaid import DUPrepaidAPIClient
from apps.orders.models import SERVICE_CHOICES, RECHARGE_TYPE, AvailableRecharge, SERVICES_PROVIDER, \
    MBME, DU_PREPAID, MINUTE, DATA, Orders, DU_POSTPAID, SALIK_DIRECT, NOL_TOPUP, ETISALAT, HAFILAT, HAFILAT_PASS, \
    HAFILAT_T_PURSE
from apps.payment.models import PaymentTransactions, PaymentMethods
from utils.exceptions import APIException400


class PaymentIntentCreateSerializer(serializers.Serializer):
    """
    Serializer to create payment intent.
    """
    amount = serializers.FloatField()
    service_type = serializers.ChoiceField(choices=SERVICE_CHOICES)
    recharge_number = serializers.CharField()
    recharge_type = serializers.ChoiceField(choices=RECHARGE_TYPE, allow_blank=True, allow_null=True)
    recharge_transaction_id = serializers.CharField(allow_blank=True, allow_null=True)
    account_pin = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    service_offered = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    current_balance = serializers.CharField(allow_null=True, required=False)
    provider_transaction_id = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    max_allowed = serializers.CharField(allow_null=True, allow_blank=True, required=True)
    product_code = serializers.CharField(allow_null=True, allow_blank=True, required=True)
    item_code = serializers.CharField(allow_null=True, allow_blank=True, required=True)

    def validate_recharge_number(self, value):
        if not value.isdigit():
            raise APIException400({
                "error": "Recharge Number is not valid"
            })
        return value

    def validate(self, attrs):
        service_type = attrs["service_type"]
        recharge_type = attrs["recharge_type"]
        amount = attrs["amount"]
        recharge_number = attrs["recharge_number"]
        # DU postpaid
        if service_type in (DU_POSTPAID, SALIK_DIRECT, NOL_TOPUP) and not attrs.get("recharge_transaction_id"):
            raise APIException400({
                "error": "recharge_transaction_id is required"
            })

        if service_type in (DU_PREPAID, HAFILAT) and not recharge_type:
            raise APIException400({
                "error": "recharge_type is required"
            })

        if service_type == HAFILAT:
            if not attrs.get("item_code") or not attrs.get("product_code"):
                raise APIException400({
                    "error": "item_code and product_code are required for Hafilat recharge"
                })

            if recharge_type not in (HAFILAT_PASS, HAFILAT_T_PURSE):
                raise APIException400({
                    "error": "recharge_type is required for Hafilat"
                })

            if recharge_type == HAFILAT_PASS and not attrs.get("max_allowed"):
                raise APIException400({
                    "error": "max_allowed is required for Hafilat"
                })


        if service_type in (SALIK_DIRECT, ETISALAT) and not attrs.get("provider_transaction_id"):
            raise APIException400({
                "error": "provider_transaction_id is required"
            })

        if service_type == SALIK_DIRECT:
            if not attrs.get("account_pin"):
                raise APIException400({
                    "error": "account_pin is required for Salik Direct"
                })
            if not int(settings.SALIK_DIRECT_MIN) <= amount <= int(settings.SALIK_DIRECT_MAX):
                raise APIException400({
                    "error": f"Invalid amount. Amount should be b/w {settings.SALIK_DIRECT_MIN}-{settings.SALIK_DIRECT_MAX}"
                })
            if not amount % 50 == 0:
                raise APIException400({
                    "error": f"Amount should be multiple of 50"
                })

        if service_type == NOL_TOPUP:
            if not int(settings.NOL_TOPUP_MIN) <= amount <= int(settings.NOL_TOPUP_MAX):
                raise APIException400({
                    "error": f"Invalid amount. Amount should be b/w {settings.NOL_TOPUP_MIN}-{settings.NOL_TOPUP_MAX}"
                })

        if service_type == ETISALAT:
            if not attrs.get("service_offered") or not attrs.get("current_balance"):
                raise APIException400({
                    "error": "Both service_offered and current_balance is required for Etisalat recharge"
                })

        # for DU prepaid
        if service_type == DU_PREPAID:
            if recharge_type == MINUTE and (
                    amount < int(settings.DU_PREPAID_MIN) or amount > int(settings.DU_PREPAID_MAX)):
                raise APIException400({
                    "error": f"Recharge amount should be between {settings.DU_PREPAID_MIN}-{settings.DU_PREPAID_MAX}"
                })
            elif recharge_type == DATA:
                # for data recharge
                qs = AvailableRecharge.objects.filter(
                    service_type=service_type,
                    recharge_type=recharge_type,
                    amount=amount,
                    is_active=True,
                    service_provider=MBME,
                    currency=settings.DEFAULT_CURRENCY
                )
                if not qs.exists():
                    raise APIException400({
                        "error": "Data recharge amount is invalid"
                    })

            status, message = DUPrepaidAPIClient().verify_customer_account(recharge_number)
            print(f"verified customer with= >{status} {message}")
            if not status:
                raise APIException400({
                    "error": message
                })

        return attrs

    class Meta:
        fields = ('amount', 'service_type', 'recharge_number', 'recharge_type', 'account_pin')


class UserPaymentHistoryListSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    def get_order_id(self, obj):
        return obj.order.order_id

    def get_amount(self, obj):
        return obj.order.amount

    def get_user_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name

    class Meta:
        model = PaymentTransactions
        fields = ("transaction_id", "created_at", "payment_provider",
                  "payment_method", "status", "amount", "order_id", "user", "user_name")


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethods
        fields = "__all__"
        read_only_fields = ("state", "id")


class PaymentMethodListSerializer(serializers.ModelSerializer):
    active_methods = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()

    def get_country_name(self, obj):
        return obj.country.name

    def get_active_methods(self, obj):
        count = 0
        count += 1 if obj.debit_card else 0
        count += 1 if obj.credit_card else 0
        count += 1 if obj.credit_points else 0
        count += 1 if obj.apple_pay else 0
        return count

    def get_city_name(self, obj):
        return obj.city.name

    class Meta:
        model = PaymentMethods
        fields = ("id", "active_methods", "country_name", "city_name", "provider")
