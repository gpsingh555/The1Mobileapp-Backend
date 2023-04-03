from django.urls import path

from rest_framework.routers import SimpleRouter
from apps.reports.views import ReportAPIView, ReportDataAPIView

router = SimpleRouter()


urlpatterns = [
    path('generate', ReportAPIView.as_view(), name='reports'),
    path('data', ReportDataAPIView.as_view(), name='report-data'),

]

urlpatterns += router.urls
