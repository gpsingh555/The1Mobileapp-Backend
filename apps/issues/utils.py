from django.db.models import Q

from apps.issues.models import UserQuery, OPEN, CLOSED
from apps.issues.serializers import QueryListSerializer, QueryPartialListSerializer
from apps.orders.utils.order_history_service import SortingFilter


class UsersQuery:
    def __init__(self, request):
        self.request = request

    def get_all_query(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = UserQuery.objects.all().order_by("-created_at")

        if self.request.GET.get('search_by'):
            qs = qs.filter(ticket_id=self.request.GET.get('search_by'))

        if self.request.GET.get('status') in (OPEN, CLOSED):
            qs = qs.filter(status=self.request.GET.get('status'))

        if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
            qs = qs.filter(
                created_at__date__gte=self.request.GET.get('from_date'),
                created_at__date__lte=self.request.GET.get('to_date')
            )

        if self.request.GET.get('sort_by') == SortingFilter.A_Z.value:
            qs = qs.order_by("user__first_name")
        elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
            qs = qs.order_by("-user__first_name")

        data["total_results"] = qs.count()
        qs = qs[offset:limit]

        data["results"] = QueryPartialListSerializer(qs, many=True).data
        return data
