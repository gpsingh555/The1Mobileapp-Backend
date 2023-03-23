from django.urls import path

from rest_framework.routers import SimpleRouter

from apps.issues.views import QueryViewSet

router = SimpleRouter()

router.register(r'query', QueryViewSet, basename='query')


urlpatterns = [

    # Admin panel apis
    # path('', CustomerBalanceAPIView.as_view(), name='postpaid-balance'),
]

urlpatterns += router.urls