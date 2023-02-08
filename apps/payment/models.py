from account.models import country, city, state
from django.db import models
from django.contrib.auth.models import User

from apps.orders.models import Orders

TRANSACTION_PROCESSING, TRANSACTION_FAILED, TRANSACTION_COMPLETED, TRANSACTION_CANCELLED = "1", "2", "3", "4"
TRANSACTION_STATUS = (
    (TRANSACTION_PROCESSING, "PROCESSING"),
    (TRANSACTION_FAILED, "FAILED"),
    (TRANSACTION_COMPLETED, "COMPLETED"),
    (TRANSACTION_CANCELLED, "CANCELLED")
)

STRIPE, PAYPAL = "1", "2"
PAYMENT_PROVIDER = (
    (STRIPE, "STRIPE"),
    (PAYPAL, "PAYPAL")
)

DEBIT_CARD, CREDIT_CARD, APPLE_PAY, CREDIT_POINTS = "1", "2", "3", "4"
PAYMENT_METHOD = (
    (DEBIT_CARD, "DEBIT_CARD"),
    (CREDIT_CARD, "CREDIT_CARD"),
    (APPLE_PAY, "APPLE_PAY"),
    (CREDIT_POINTS, "CREDIT_POINTS")
)

USER, SELLER = "1", "2"
PAYMENT_METHOD_PROVIDER = (
    (USER, "USER"),
    (SELLER, "SELLER")
)


class StripeCustomer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='stripe_customer')
    customer_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stripe_customer'

    def __str__(self):
        return str(self.user.id)


class PaymentMethods(models.Model):
    country = models.ForeignKey(country, on_delete=models.CASCADE, related_name='country_payment_method')
    state = models.ForeignKey(state, on_delete=models.CASCADE, related_name='state_payment_method', blank=True, null=True)
    city = models.ForeignKey(city, on_delete=models.CASCADE, related_name='city_payment_method', blank=True, null=True)
    debit_card = models.BooleanField(default=True)
    credit_card = models.BooleanField(default=True)
    apple_pay = models.BooleanField(default=True)
    credit_points = models.BooleanField(default=True)
    provider = models.CharField(max_length=20, choices=PAYMENT_METHOD_PROVIDER)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_methods'
        unique_together = ('country', 'city', 'provider')

    def __str__(self):
        return str(self.id)


class PaymentTransactions(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payment')
    transaction_id = models.CharField(unique=True, max_length=100)

    payment_provider = models.CharField(max_length=50, choices=PAYMENT_PROVIDER)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, blank=True, null=True)
    payment_intent = models.CharField(max_length=500)
    gateway_response = models.TextField()
    status = models.CharField(max_length=50, choices=TRANSACTION_STATUS)
    amount_paid = models.FloatField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_transactions'

    def __str__(self):
        return str(self.id)

