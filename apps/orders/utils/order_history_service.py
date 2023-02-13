import datetime

from enum import Enum

from django.db.models import Sum
from django.utils import timezone

from apps.orders.models import Orders, DU_PREPAID, DU_POSTPAID, SALIK_DIRECT, HAFILAT, NOL_TOPUP, ETISALAT
from apps.orders.serializers import OrderListSerializer, OrderDetailSerializer, OrderListViewSerializer
from utils.exceptions import APIException400, APIException404


class SortingFilter(Enum):
    A_Z = "1"
    Z_A = "2"


class MonthFilter(Enum):
    TODAY = "1"
    THIS_WEEK = "2"
    THIS_MONTH = "3"
    THIS_YEAR = "4"
    ANY = "5"


class OrderHistoryCategory(Enum):
    ALL = '0'
    DU = "1"
    ETISALAT = "3"
    NOL_TOPUP = "4"
    HAFILAT = "5"
    SALIK_DIRECT = "6"


class ORDER_TYPE(Enum):
    MOBILE = "1"
    TRANSPORT = "2"
    ANY = "3"


class OrderHistory:

    def __init__(self, request):
        self.request = request

    def get_order_list(self):
        """1-mobile recharge, 2-transport recharge, 3-all"""
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}
        if not self.request.GET.get('order_type'):
            raise APIException400({
                "error": "order_type is required"
            })

        if self.request.GET.get('order_type') in (ORDER_TYPE.MOBILE.value, ORDER_TYPE.ANY.value):
            qs = Orders.objects.filter(user=self.request.user)
            if self.request.GET.get('search_by'):
                print(self.request.GET.get('search_by'))
                qs = qs.filter(order_id=self.request.GET.get('search_by'))

            in_filter = []
            if self.request.GET.get('category') in (OrderHistoryCategory.DU.value, OrderHistoryCategory.ALL.value):
                in_filter = [DU_PREPAID, DU_POSTPAID]

            elif self.request.GET.get('category') in (OrderHistoryCategory.ETISALAT.value, OrderHistoryCategory.ALL.value):
                in_filter.append(ETISALAT)

            qs = qs.filter(
                service_type__in=in_filter
            ).order_by("-created_at")

            if self.request.GET.get('month') == MonthFilter.TODAY.value:
                qs = qs.filter(created_at__date=timezone.now().today())
            elif self.request.GET.get('month') == MonthFilter.THIS_WEEK.value:
                qs = qs.filter(created_at__week=timezone.now().isocalendar()[1])
            elif self.request.GET.get('month') == MonthFilter.THIS_MONTH.value:
                qs = qs.filter(created_at__month=timezone.now().month)
            elif self.request.GET.get('month') == MonthFilter.THIS_YEAR.value:
                qs = qs.filter(created_at__year=timezone.now().year)

            #data["total_results"] = qs.count()
            qs = qs[offset:limit + offset]
            data["mobile_recharge"] = OrderListSerializer(qs, many=True).data

        if self.request.GET.get('order_type') in (ORDER_TYPE.TRANSPORT.value, ORDER_TYPE.ANY.value):

            qs = Orders.objects.filter(user=self.request.user)
            if self.request.GET.get('search_by'):
                print(self.request.GET.get('search_by'))
                qs = qs.filter(order_id=self.request.GET.get('search_by'))

            in_filter = []
            if self.request.GET.get('category') == OrderHistoryCategory.SALIK_DIRECT.value:
                in_filter.append(SALIK_DIRECT)
            elif self.request.GET.get('category') == OrderHistoryCategory.HAFILAT.value:
                in_filter.append(HAFILAT)
            elif self.request.GET.get('category') == OrderHistoryCategory.NOL_TOPUP.value:
                in_filter.append(NOL_TOPUP)
            elif self.request.GET.get('category') == OrderHistoryCategory.ALL.value:
                in_filter = [ETISALAT, HAFILAT, NOL_TOPUP, SALIK_DIRECT]

            if self.request.GET.get('month') == MonthFilter.TODAY.value:
                qs = qs.filter(created_at__date=timezone.now().today())
            elif self.request.GET.get('month') == MonthFilter.THIS_WEEK.value:
                qs = qs.filter(created_at__week=timezone.now().isocalendar()[1])
            elif self.request.GET.get('month') == MonthFilter.THIS_MONTH.value:
                qs = qs.filter(created_at__month=timezone.now().month)
            elif self.request.GET.get('month') == MonthFilter.THIS_YEAR.value:
                qs = qs.filter(created_at__year=timezone.now().year)

            qs = qs.filter(
                service_type__in=in_filter
            ).order_by("-created_at")
            #data["total_results"] = qs.count()
            qs = qs[offset:limit + offset]
            data["transport_recharge"] = OrderListSerializer(qs, many=True).data

        return data

    def get_order_detail(self):
        qs = Orders.objects.filter(user=self.request.user,
                                   order_id=self.request.GET.get('order_id')).prefetch_related(
            "order_detail", "payment")
        if not qs.exists():
            raise APIException404({
                "error": "no resource found"
            })
        data = OrderDetailSerializer(qs, many=True).data
        return data

    def get_order_list_for_admin(self):

        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = Orders.objects.filter()

        if self.request.GET.get('search_by'):
            if self.request.GET.get('search_by').isdigit():
                qs = qs.filter(user=self.request.GET.get('search_by'))
            else:
                qs = qs.filter(order_id=self.request.GET.get('search_by'))

        if self.request.GET.get('category_filter') == ORDER_TYPE.MOBILE.value:
            qs = qs.filter(service_type__in=[DU_PREPAID, DU_POSTPAID, ETISALAT])
        elif self.request.GET.get('category_filter') == ORDER_TYPE.TRANSPORT.value:
            qs = qs.filter(service_type__in=[SALIK_DIRECT, HAFILAT, NOL_TOPUP])

        if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
            qs = qs.filter(
                created_at__date__gte=self.request.GET.get('from_date'),
                created_at__date__lte=self.request.GET.get('to_date')
            )

        if self.request.GET.get('filter_by') == MonthFilter.TODAY.value:
            qs = qs.filter(created_at__date=timezone.now().today())
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_WEEK.value:
            qs = qs.filter(created_at__week=timezone.now().isocalendar()[1])
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_MONTH.value:
            qs = qs.filter(created_at__month=timezone.now().month)
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_YEAR.value:
            qs = qs.filter(created_at__year=timezone.now().year)

        if self.request.GET.get('sort_by') == SortingFilter.A_Z.value:
            qs = qs.order_by("id")
        elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
            qs = qs.order_by("-id")

        data["total_results"] = qs.count()
        qs = qs[offset:limit]

        data["results"] = OrderListViewSerializer(qs, many=True).data
        return data