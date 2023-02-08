"""
"""
from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.payment.views import StripePaymentAPIView, StripeWebhookAPIView, StripePaymentView, PaymentUserListAPIView, \
    UserPaymentHistoryListAPIView, PaymentMethodViewSet

router = SimpleRouter()

router.register(r'payment-method', PaymentMethodViewSet, basename='payment-method')


urlpatterns = [
    path('stripe/initiate', StripePaymentAPIView.as_view(), name='stripe-initiate-payment'),
    path('stripe/webhook', StripeWebhookAPIView.as_view(), name='stripe-webhook'),
    path('stripe/payment', StripePaymentView.as_view(), name='stripe-payment'),

    # Admin panel API
    path('users', PaymentUserListAPIView.as_view(), name='payment-users'),
    path('users/<user_id>', UserPaymentHistoryListAPIView.as_view(), name='payment-by-users'),

]

urlpatterns += router.urls
