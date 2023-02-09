from enum import Enum

from django.db.models import F, Sum, Count, Q
from django.utils import timezone

from apps.orders.models import DU_PREPAID, DU_POSTPAID
from apps.orders.utils.order_history_service import MonthFilter, ORDER_TYPE, SortingFilter
from apps.payment.models import PaymentTransactions, DEBIT_CARD, CREDIT_CARD, APPLE_PAY, CREDIT_POINTS, \
    TRANSACTION_CANCELLED
from apps.payment.serializers import UserPaymentHistoryListSerializer


class PaymentManagementService:

    def __init__(self, request):
        self.request = request

    def get_latest_payment_users(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = PaymentTransactions.objects.annotate(
            first_name=F('user__first_name'),
            last_name=F('user__last_name'),
            email=F('user__email'),
            mobile=F('user__username'),
            country=F('user__user_profile__country'),
            state=F('user__user_profile__state'),
            city=F('user__user_profile__city'),
        ).values(
            "user", "first_name", "last_name", "email", "mobile",
            "country", "state", "city")

        if self.request.GET.get('search_by'):
            if self.request.GET.get('search_by').isdigit():
                qs = qs.filter(user=self.request.GET.get('search_by'))
            else:
                qs = qs.filter(first_name__icontains=self.request.GET.get('search_by'))

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
            qs = qs.filter(created_at__month=timezone.now().now().month)
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_YEAR.value:
            qs = qs.filter(created_at__year=timezone.now().now().year)

        data["total_results"] = qs.count()
        qs = qs.distinct()[offset:limit]

        return qs

    def get_user_transactions(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = PaymentTransactions.objects.filter(user=self.request.user)

        if self.request.GET.get('search_by'):
            qs = qs.filter(transaction_id=self.request.GET.get('search_by'))

        if self.request.GET.get('category_filter') == ORDER_TYPE.MOBILE.value:
            qs = qs.filter(order__service_type__in=[DU_PREPAID, DU_POSTPAID])
        elif self.request.GET.get('category_filter') == ORDER_TYPE.TRANSPORT.value:
            qs = qs.filter(order__service_type__in=[])

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
            qs = qs.order_by("transaction_id")
        elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
            qs = qs.order_by("-transaction_id")

        data["total_results"] = qs.count()
        qs = qs[offset:limit]

        data["total_amount"] = qs.aggregate(Sum('order__amount')).get("order__amount__sum")

        data["results"] = UserPaymentHistoryListSerializer(qs, many=True).data
        return data

    def get_payment_stats(self):

        qs = PaymentTransactions.objects.filter().exclude(status=TRANSACTION_CANCELLED)

        if self.request.GET.get('country'):
            qs = qs.filter(user__user_address__country__iexact=self.request.GET.get('country'))

        if self.request.GET.get('city'):
            qs = qs.filter(user__user_address__city__iexact=self.request.GET.get('city'))

        if self.request.GET.get('filter_by') == MonthFilter.TODAY.value:
            qs = qs.filter(created_at__date=timezone.now().today())
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_WEEK.value:
            qs = qs.filter(created_at__week=timezone.now().isocalendar()[1])
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_MONTH.value:
            qs = qs.filter(created_at__month=timezone.now().month)
        elif self.request.GET.get('filter_by') == MonthFilter.THIS_YEAR.value:
            qs = qs.filter(created_at__year=timezone.now().year)

        qs = qs.values('payment_method').annotate(
            dcount=Count('payment_method'),
        )

        f_data = {"credit_card": 0, "debit_card": 0, "apple_pay": 0, "credit_points": 0}
        total = 0
        for data in qs:
            total += data.get("dcount")

        if total:
            for data in qs:
                if data.get("payment_method") == DEBIT_CARD:
                    f_data["debit_card"] = round((data.get("dcount") / total) * 100, 2)
                elif data.get("payment_method") == CREDIT_CARD:
                    f_data["credit_card"] = round((data.get("dcount") / total) * 100, 2)
                elif data.get("payment_method") == APPLE_PAY:
                    f_data["apple_pay"] = round((data.get("dcount") / total) * 100, 2)
                elif data.get("payment_method") == CREDIT_POINTS:
                    f_data["credit_points"] = round((data.get("dcount") / total) * 100, 2)

        return f_data
