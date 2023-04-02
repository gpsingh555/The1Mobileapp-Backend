from django.db.models import Q, Sum

from apps.chat.models import UserChatHistory, ChatGroup, UserAudioVideoCallHistory, AUDIO, VIDEO
from apps.chat.serializers import UserChatHistoryDetailSerializer, UserGroupHistoryDetailSerializer, \
    UserAudioVideoHistoryDetailSerializer
from apps.orders.utils.order_history_service import SortingFilter


class ChatHistory:
    def __init__(self, request):
        self.request = request

    def get_user_chat(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = UserChatHistory.objects.all().order_by("-created_at")

        if self.request.GET.get('search_by'):
            qs = qs.filter(Q(chat_init_user__first_name=self.request.GET.get('search_by')) |
                           Q(second_user__first_name=self.request.GET.get('search_by')))

        if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
            qs = qs.filter(
                created_at__date__gte=self.request.GET.get('from_date'),
                created_at__date__lte=self.request.GET.get('to_date')
            )

        if self.request.GET.get('sort_by') == SortingFilter.A_Z.value:
            qs = qs.order_by("chat_init_user__first_name", "chat_init_user__last_name")
        elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
            qs = qs.order_by("-chat_init_user__first_name", "-chat_init_user__last_name")

        data["total_results"] = qs.count()
        qs = qs[offset:limit]

        data["results"] = UserChatHistoryDetailSerializer(qs, many=True).data
        return data

    def get_group_history(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = ChatGroup.objects.all().order_by("-created_at")

        if self.request.GET.get('search_by'):
            qs = qs.filter(name=self.request.GET.get('search_by'))

        if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
            qs = qs.filter(
                created_at__date__gte=self.request.GET.get('from_date'),
                created_at__date__lte=self.request.GET.get('to_date')
            )

        if self.request.GET.get('sort_by') == SortingFilter.A_Z.value:
            qs = qs.order_by("name")
        elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
            qs = qs.order_by("-name")

        data["total_results"] = qs.count()
        qs = qs[offset:limit]

        data["results"] = UserGroupHistoryDetailSerializer(qs, many=True).data
        return data

    def get_audio_video_history(self):
        limit = int(self.request.GET.get('limit', 10))
        offset = int(self.request.GET.get('offset', 0))
        data = {"limit": limit, "offset": offset}

        qs = UserAudioVideoCallHistory.objects.all().order_by("-created_date")

        if self.request.GET.get('call_type') in (AUDIO, VIDEO):
            qs = qs.filter(call_type=self.request.GET.get('call_type'))

        if self.request.GET.get('search_by'):
            qs = qs.filter(name=self.request.GET.get('search_by'))

        if self.request.GET.get('from_date') and self.request.GET.get('to_date'):
            qs = qs.filter(
                created_date__date__gte=self.request.GET.get('from_date'),
                created_date__date__lte=self.request.GET.get('to_date')
            )

        if self.request.GET.get('sort_by') == SortingFilter.A_Z.value:
            qs = qs.order_by("sender")
        elif self.request.GET.get('sort_by') == SortingFilter.Z_A.value:
            qs = qs.order_by("-sender")

        data["total_results"] = qs.count()
        qs = qs[offset:limit]

        data["results"] = UserAudioVideoHistoryDetailSerializer(qs, many=True).data
        return data
