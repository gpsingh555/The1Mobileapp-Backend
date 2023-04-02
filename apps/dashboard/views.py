from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.dashboard.utils import Dashboard
from utils.response import response


class DashboardAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = Dashboard(request).get_dashboard_data()
        return response(data=data, message='success')
