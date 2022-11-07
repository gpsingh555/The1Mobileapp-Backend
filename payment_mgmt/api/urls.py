from django.urls import path
from .views import *
from django.conf import settings

urlpatterns = [
    path('auth_token',auth_token.as_view()),
    path('balance_and_Payment',balance_and_Payment.as_view()),
    path('merchant_transaction_report',merchant_transaction_report.as_view()),
    path('merchant_pending_transaction',merchant_pending_transaction.as_view()),
    path('merchant_check_status_transactionid',merchant_check_status_transactionid.as_view()),
    path('repost_pending_transaction',repost_pending_transaction.as_view()),
    path('merchant_balance_check',merchant_balance_check.as_view()),
    path('transaction_list',transaction_list.as_view)
]