"""
"""
import stripe

from django.conf import settings
from django.urls import reverse

import logging

from apps.payment.models import StripeCustomer, PaymentTransactions
from utils.decorator import exception_handler

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Stripe(object):
    """
    Stripe
    """

    def __init__(self):
        self._configure()
        stripe.api_key = self.api_key

    def _configure(self):
        """ configure stripe keys """
        self.api_key = settings.STRIPE_CLIENT_SECRET

    @exception_handler
    def create_payment_intent(self, *args, **kwargs):
        """
        Method to create payment intent
        """
        amount = kwargs.get('amount', 0)
        currency = kwargs.get('currency', '')
        receipt_email = kwargs.get('receipt_email', None)
        user = kwargs.get("user")

        meta_data = {
            'order_id': kwargs.get('order_id', ''),
            'user_id': user.id,
            'service_type': kwargs.get("service_type"),
            'recharge_number': kwargs.get("recharge_number"),
            "service_provider": kwargs.get("service_provider"),
            'recharge_type': kwargs.get("recharge_type"),
            'recharge_transaction_id': kwargs.get("recharge_transaction_id"),
            'amount': amount,
            'account_pin': kwargs.get("account_pin"),
            'service_offered': kwargs.get("service_offered"),
            'current_balance': kwargs.get("current_balance"),
            'currency': currency,
            'provider_transaction_id': kwargs.get("provider_transaction_id"),
            'max_allowed': kwargs.get("max_allowed"),
            'product_code': kwargs.get("product_code"),
            'item_code': kwargs.get("item_code"),
        }
        customer_id = self.__get_or_create_customer(user)
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency,
            # payment_method_types=['card'],
            automatic_payment_methods={
                'enabled': True,
            },
            customer=customer_id,
            description="Payment for mobile recharge",
            receipt_email=receipt_email,
            metadata=meta_data,
            # setup_future_usage='on_session',
            return_url=None,
        )
        # data = (settings.SITE_URL + reverse('stripe-payment')
        #                 + '?intent_id=' + intent['id'])
        data = {
            "payment_intent": intent['id'],
            "customer": customer_id,
            "publish_key": settings.STRIP_PUBLISHABLE_KEY,
            "client_secret": intent["client_secret"],
            "ephemeral_key": self.get_ephemeralKey(customer_id)
        }
        return data

    def __get_or_create_customer(self, user):
        objs = StripeCustomer.objects.filter(user=user)
        if objs.exists():
            return objs[0].customer_id

        customer = stripe.Customer.create(
            address={"line1": 'Text address'},
            email=user.email,
            metadata={},
            name=user.first_name
        )

        obj = StripeCustomer.objects.create(
            user_id=user.id,
            customer_id=customer.id,
        )

        return obj.customer_id

    def get_ephemeralKey(self, customer_id):
        ephemeralKey = stripe.EphemeralKey.create(
            customer=customer_id,
            stripe_version='2022-11-15',
        )
        return ephemeralKey["secret"]

    @exception_handler
    def retrive_payment_intent(self, *args, **kwargs):
        """
        """
        intent_id = kwargs.get('intent_id')
        intent = stripe.PaymentIntent.retrieve(
            intent_id,
        )
        return intent

    def get_or_create_customer(self, *args, **kwargs):
        """
        """
        name = kwargs.get('name')
        address = kwargs.get("address")
        email = kwargs.get("email")
        customer = stripe.Customer.create(
            address=address,
            email=email,
            name=name
        )
        return customer

    def cancel_payment_intent(self, *args, **kwargs):
        """
        To cancel payemnt intent
        """
        intent_id = kwargs.get('intent_id')
        intent = stripe.PaymentIntent.cancel(
            intent_id,
        )
        return intent

