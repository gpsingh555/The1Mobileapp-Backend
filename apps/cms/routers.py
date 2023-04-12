
from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.cms.views import CMSAPIView, StaticPagesForApplicationView

router = SimpleRouter()

urlpatterns = [
    path('', CMSAPIView.as_view(), name='cms'),
    path('static', StaticPagesForApplicationView, name='cms-view')
    # path('', StaticPagesForApplicationView, name='cms-view')

]

urlpatterns += router.urls
