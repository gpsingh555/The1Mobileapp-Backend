from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UserCreditPoint(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_points')
    credit_points=models.IntegerField(default=0)
    updated_on=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user.id) +'-'+str(self.id)


class CreditPointTransaction(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_transactions')
    transaction_id=models.AutoField(primary_key=True,unique=True)
    reason_title=models.CharField(max_length=100, default='')
    reason_desc=models.TextField(null=True,blank=True)
    order_id=models.CharField(max_length=10,null=True,blank=True, default=None)
    referral_id=models.CharField(null=True, blank=True,default=None, max_length=10)
    debited_points=models.IntegerField(default=0)
    credited_points=models.IntegerField(default=0)
    transaction_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.transaction_id)














