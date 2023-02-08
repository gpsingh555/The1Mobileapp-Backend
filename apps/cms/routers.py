
from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.cms.views import CMSAPIView

router = SimpleRouter()

urlpatterns = [
    path('', CMSAPIView.as_view(), name='cms')
]

urlpatterns += router.urls
