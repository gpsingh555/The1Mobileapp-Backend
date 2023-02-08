from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from account.cron import upload_news
from apps.orders.api_clients.du_postpaid import DUPostpaidAPIClient
from apps.orders.api_clients.du_prepaid import DUPrepaidAPIClient
from apps.orders.api_clients.etisalat import EtisalatAPIClient
from apps.orders.api_clients.hafilat import HafilatAPIClient
from apps.orders.api_clients.nol_topup import NOLTopupAPIClient
from apps.orders.api_clients.salik_direct import SalikDirectAPIClient
from apps.orders.models import AvailableRecharge, MBME, Orders
from apps.orders.serializers import PlaceOrderSerializer, OrderDetailSerializer, \
    OrderDetailViewSerializer, OrderListViewSerializer, ValidateNOLSerializer, ValidateSalikDirectSerializer, \
    ValidateEtisalatSerializer, ValidateHafilatSerializer
from apps.orders.utils.order_history_service import OrderHistory
from apps.orders.utils.order_place_service import OrderService
from utils.exceptions import APIException400
from utils.response import response


# Create your views here.

class PlaceOrderAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status, msg = OrderService(request.data.get("payment_intent_id"), request).place_order()
        return response(data={"status": status}, message=msg)


class AvailableRechargeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        service_type = self.request.GET.get('service_type')
        service_provide = MBME
        if service_type:
            data = AvailableRecharge.objects.filter(
                is_active=True, service_type=service_type, service_provider=service_provide).values(
                "amount", "currency", "detail", "validity", "full_description").order_by('amount')
            resp = {"data_recharge": data}
            return response(message="success", data=resp)
        raise APIException400({
            "error": "service_type is required"
        })


class OrdersHistoryListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = OrderHistory(request).get_order_list()
        return response(message="success", data=data)


class OrdersHistoryDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not self.request.GET.get('order_id'):
            raise APIException400({
                "error": "order_id is required"
            })
        data = OrderHistory(request).get_order_detail()
        return response(message="success", data=data)


class DUPostpaidBalanceAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        number = self.request.GET.get('number')
        if number:
            if not number.isdigit() or len(number) > 10:
                raise APIException400({
                    "error": "Invalid mobile Number"
                })
            data = DUPostpaidAPIClient().get_customer_balance(number)
            return response(message="success", data=data)
        raise APIException400({
            "error": "number is required"
        })


class VerifyDUPrepaidAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        number = self.request.GET.get('number')
        if number:
            if not number.isdigit() or len(number) > 10:
                raise APIException400({
                    "error": "Invalid mobile Number"
                })
            status, msg = DUPrepaidAPIClient().verify_customer_account(number)
            if not status:
                raise APIException400({
                    "error": msg
                })
            return response(message=msg)
        raise APIException400({
            "error": "number is required"
        })


class VerifyNOLCustomerAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        card_number = self.request.GET.get('card_number')
        amount = self.request.GET.get('amount')
        serializer = ValidateNOLSerializer(data={"card_number": card_number, "amount": amount})
        serializer.is_valid(raise_exception=True)

        msg, data = NOLTopupAPIClient().verify_customer_card(card_number, amount)
        return response(message=msg, data=data)


class VerifySalikDirectCustomerAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = {"account_number": self.request.GET.get('account_number'),
                "account_pin": self.request.GET.get('account_pin'), "amount": self.request.GET.get('amount')}

        serializer = ValidateSalikDirectSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        status, msg, data = SalikDirectAPIClient().verify_customer_card(
            serializer.validated_data["account_number"],
            serializer.validated_data["account_pin"],
        )
        return response(message=msg, data=data)


class VerifyHafilatCustomerAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = {"card_number": self.request.GET.get('card_number'),
                }
        serializer = ValidateHafilatSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        msg, data = HafilatAPIClient().verify_customer_card(
            serializer.validated_data["card_number"],
        )
        return response(message=msg, data=data)


class VerifyEtisalatCustomerAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = {"account_number": self.request.GET.get('account_number'),
                "service_offered": self.request.GET.get('service_offered')}
        serializer = ValidateEtisalatSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        msg, data = EtisalatAPIClient().verify_customer_account(
            serializer.validated_data["account_number"],
            serializer.validated_data["service_offered"],
        )
        return response(message=msg, data=data)



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrderListViewSerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('created_at',)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailViewSerializer
        return super(OrderViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        response_data = OrderHistory(request).get_order_list_for_admin()
        return response(data=response_data, message="success")

    def retrieve(self, request, *args, **kwargs):
        response_data = super(OrderViewSet, self).retrieve(request, *args, **kwargs).data
        return response(data=response_data, message="success")
