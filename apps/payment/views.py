from django.conf import settings
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import SERVICES_PROVIDER, Orders
from apps.payment.models import PaymentTransactions, PaymentMethods
from apps.payment.serializers import PaymentIntentCreateSerializer, PaymentMethodSerializer, PaymentMethodListSerializer
from apps.payment.utils.payment_managent_service import PaymentManagementService
from apps.payment.utils.stripe import Stripe
from apps.payment.utils.webhooks import StripeWebhook
from utils.response import response


class StripePaymentView(View):
    """
    View to create payment link
    """

    def get(self, request, *args, **kwargs):
        """
        """
        stripe_obj = Stripe()
        intent_id = request.GET.get('intent_id')
        context = {}
        if intent_id:
            # check payment intent
            stripe_obj = Stripe()
            response = stripe_obj.retrive_payment_intent(
                intent_id=intent_id
            )
            # if invoice is already paid then cancel the intent
            # if response.get('status') != 'canceled':
            #     response = stripe_obj.cancel_payment_intent(
            #         intent_id=intent_id)

            print(response)
            if response["data"].get('status') in ("requires_payment_method", "requires_source"):
                secret_id = response["data"]['client_secret']
                amount = response["data"]['metadata']['amount']
            else:
                print(response)
                return render(request, 'expire.html', context)

            context = {
                'client_secret': secret_id,
                'stripe_pub_key': settings.STRIP_PUBLISHABLE_KEY,
                'amount': amount,
                'success_url': ""
            }
            return render(request, 'payment.html', context)
        return render(request, 'expire.html', context)


class StripePaymentAPIView(APIView):
    """
    Create Payment intent
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        """
        user = request.user
        serializer = PaymentIntentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # stripe payment
        stripe_obj = Stripe()
        resp = stripe_obj.create_payment_intent(
            user=user,
            amount=serializer.validated_data.get('amount'),
            currency=settings.DEFAULT_CURRENCY,
            service_type=serializer.validated_data.get("service_type"),
            recharge_number=serializer.validated_data.get("recharge_number"),
            recharge_type=serializer.validated_data.get("recharge_type"),
            service_provider=SERVICES_PROVIDER[0][0],
            recharge_transaction_id=serializer.validated_data.get('recharge_transaction_id'),
            account_pin=serializer.validated_data.get('account_pin'),
            service_offered=serializer.validated_data.get('service_offered'),
            current_balance=serializer.validated_data.get('current_balance'),
            provider_transaction_id=serializer.validated_data.get('provider_transaction_id'),
            max_allowed=serializer.validated_data.get('max_allowed'),
            product_code=serializer.validated_data.get('product_code'),
            item_code=serializer.validated_data.get('item_code'),

        )
        return response(message=resp["detail"], status_code=resp['status_code'], data=resp["data"])


class StripeWebhookAPIView(APIView):
    """
    method for handle events on stripe
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        """
        data = request.data
        webhook_obj = StripeWebhook()
        event_type = webhook_obj.get_event(data)
        if event_type:
            if event_type in ('payment_intent.succeeded',
                              'payment_intent.payment_failed', 'payment_intent.processing'):
                webhook_obj.connect_payment_update_hook(data)

        return Response(status=204)


class PaymentUserListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = PaymentManagementService(request).get_latest_payment_users()
        return response(data=data, message="success")


class UserPaymentHistoryListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = PaymentManagementService(request).get_user_transactions()
        return response(data=data, message="success")


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethods.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('created_at',)

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentMethodListSerializer
        return super(PaymentMethodViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        response_data = super(PaymentMethodViewSet, self).list(request, *args, **kwargs)
        return response(data=response_data.data, message="success")

    def create(self, request, *args, **kwargs):
        super(PaymentMethodViewSet, self).create(request, *args, **kwargs)
        return response(message="created successfully")

    def retrieve(self, request, *args, **kwargs):
        response_data = super(PaymentMethodViewSet, self).retrieve(request, *args, **kwargs).data
        return response(data=response_data, message="success")

    def update(self, request, *args, **kwargs):
        super(PaymentMethodViewSet, self).update(request, *args, **kwargs)
        return response(message="updated successfully")

    @action(detail=False, methods=['get'])
    def stat(self, request):
        data = PaymentManagementService(request).get_payment_stats()
        return response(data=data, message="success")
