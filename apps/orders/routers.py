"""
"""
from django.conf.urls import url
from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.orders.views import PlaceOrderAPIView, AvailableRechargeAPIView, OrdersHistoryListAPIView, \
    DUPostpaidBalanceAPIView, OrdersHistoryDetailAPIView, OrderViewSet, VerifyDUPrepaidAPIView, \
    VerifyNOLCustomerAPIView, VerifySalikDirectCustomerAPIView, VerifyHafilatCustomerAPIView, \
    VerifyEtisalatCustomerAPIView

router = SimpleRouter()

router.register(r'', OrderViewSet, basename='order')


urlpatterns = [
    path('place', PlaceOrderAPIView.as_view(), name='order-place'),
    path('available/recharge', AvailableRechargeAPIView.as_view(), name='available-recharge'),
    path('history', OrdersHistoryListAPIView.as_view(), name='order-history'),
    path('history/detail', OrdersHistoryDetailAPIView.as_view(), name='order-history-detail'),
    path('postpaid/balance', DUPostpaidBalanceAPIView.as_view(), name='postpaid-balance'),
    path('verify/prepaid', VerifyDUPrepaidAPIView.as_view(), name='verify-prepaid'),
    path('verify/nol-card', VerifyNOLCustomerAPIView.as_view(), name='verify-nol-card'),
    path('verify/salik-account', VerifySalikDirectCustomerAPIView.as_view(), name='verify-satic-account'),
    path('verify/hafilat-card', VerifyHafilatCustomerAPIView.as_view(), name='verify-hafilat-card'),
    path('verify/etisalat', VerifyEtisalatCustomerAPIView.as_view(), name='verify-etisalat'),

    # Admin panel apis
    # path('', CustomerBalanceAPIView.as_view(), name='postpaid-balance'),
]

urlpatterns += router.urls
