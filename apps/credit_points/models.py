from django.db import models
from django.contrib.auth.models import User

from apps.orders.models import Orders

CREDITED, DEBITED = "1", "2"
TRANS_TYPE = (
    (CREDITED, "CREDITED"),
    (DEBITED, "DEBITED")
)

EARN_BY_REFERRAL, EARN_BY_ORDER = "1", "2"
CREDIT_EARN_TYPE = (
    (EARN_BY_REFERRAL, "EARN_BY_REFERRAL"),
    (EARN_BY_ORDER, "EARN_BY_ORDER")
)


class UserCreditPoint(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_credit_points')
    credit_points = models.IntegerField(default=0)
    user_referral_code = models.CharField(unique=True, max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.id) + '-' + str(self.credit_points)


class CreditPointTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_credit_point_trans')
    trans_type = models.CharField(max_length=2, choices=TRANS_TYPE)
    credit_type = models.CharField(max_length=2, choices=CREDIT_EARN_TYPE)
    credit_points = models.IntegerField(default=0)

    # optional field when order placed
    equ_amount_paid = models.FloatField(default=0, blank=True, null=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE,
                              blank=True, null=True, related_name='credit_point_trans')

    # optional when order
    earn_from_user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                       related_name='earn_by_user_credit_points')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
