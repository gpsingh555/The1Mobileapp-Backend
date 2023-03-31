#
#
# class ChatHistory:
#     def __init__(self, request):
#         self.request = request
#
#     def get_user_transactions(self, user_id):
#         limit = int(self.request.GET.get('limit', 10))
#         offset = int(self.request.GET.get('offset', 0))
#         data = {"limit": limit, "offset": offset}
#
#         qs = .objects.all()
#
#         if self.request.GET.get('search_by'):
#             qs = qs.filter(transaction_id=self.request.GET.get('search_by'))
#
#         if self.request.GET.get('category_filter') == ORDER_TYPE.MOBILE.value:
#             qs = qs.filter(order__service_type__in=[DU_PREPAID, DU_POSTPAID])
#         elif self.request.GET.get('category_filter') == ORDER_TYPE.TRANSPORT.value:
#             qs = qs.filter(order__service_type__in=[])
#
#         if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
#             qs = qs.filter(
#                 created_at__date__gte=self.request.GET.get('from_date'),
#                 created_at__date__lte=self.request.GET.get('to_date')
#             )
#
#         if self.request.GET.get('filter_by') == MonthFilter.TODAY.value:
#             qs = qs.filter(created_at__date=timezone.now().today())
#         elif self.request.GET.get('filter_by') == MonthFilter.THIS_WEEK.value:
#             qs = qs.filter(created_at__week=timezone.now().isocalendar()[1])
#         elif self.request.GET.get('filter_by') == MonthFilter.THIS_MONTH.value:
#             qs = qs.filter(created_at__month=timezone.now().month)
#         elif self.request.GET.get('filter_by') == MonthFilter.THIS_YEAR.value:
#             qs = qs.filter(created_at__year=timezone.now().year)
#
#         if self.request.GET.get('sort_by') == SortingFilter.A_Z.value:
#             qs = qs.order_by("transaction_id")
#         elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
#             qs = qs.order_by("-transaction_id")
#
#         data["total_results"] = qs.count()
#         qs = qs[offset:limit]
#
#         data["total_amount"] = qs.aggregate(Sum('order__amount')).get("order__amount__sum")
#
#         data["results"] = UserPaymentHistoryListSerializer(qs, many=True).data
#         return data