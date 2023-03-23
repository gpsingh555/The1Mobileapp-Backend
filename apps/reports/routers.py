from django.urls import path

from rest_framework.routers import SimpleRouter
from apps.reports.views import ReportAPIView

router = SimpleRouter()


urlpatterns = [
    path('generate', ReportAPIView.as_view(), name='reports'),
]

urlpatterns += router.urls
