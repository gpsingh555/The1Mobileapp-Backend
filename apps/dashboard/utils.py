from django.db.models import Count, Q
from django.contrib.auth.models import User



class Dashboard:
    def __init__(self, request):
        self.request = request

    def get_dashboard_data(self):
        # users
        data = {}
        data["user_data"] = User.objects.aggregate(
            active_users=Count(filter=Q(user__is_active=True)),
            inactive_users=Count(filter=Q(user__is_active=False)),
            total_users=Count(filter=Q(user__is_active=False)),
        )
        # orders

        # revenues

        return data
