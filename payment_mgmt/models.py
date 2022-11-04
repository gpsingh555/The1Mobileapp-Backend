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

class GenerateToken(models.Model):
    status=models.CharField(max_length=100,default='')
    access_token=models.CharField(max_length=100,default='')
    expiresin=models.IntegerField(max_length=100,default=0)
    tokentype=models.BooleanField(max_length=50,default=0)
    walletbalance=models.IntegerField(max_length=100,default=0)

    def __str__(self):
        return str(self.access_token)
        
class WalletBalance(models.Models):
    transaction_id=models.AutoField(primary_key=True,unique=True)
    username=models.TextField(null=True,blank=True)
    balance=models.IntegerField(max_length=10,null=True,blank=True, default=None)
    response_message=models.IntegerField(null=True, blank=True,default=None, max_length=10)

    def __str__(self):
        return str(self.transaction_id)

class Transaction_report(models.Model):
    from_date=models.IntegerField(max_length=50,default=0)
    to_date=models.IntegerField(max_length=50,default=0)

    def __str__(self):
        return str(self.transaction_report)

class Find_my_transaction_id(models.model):
    transaction_id=models.AutoField(primary_key=True,unique=True)
    transaction_status=models.CharField(max_length=10,default=0)

    def __str__(self):
        return str(self.transaction_id)

class All_Pending_Transaction(models.Model):
    from_date=models.IntegerField(max_length=20, default=0)
    to_date=models.IntegerField(max_length=20,default=0)

    def __str__(self):
        return str(self.All_Pending_Transaction)

class Process_Pending_Payment(models.Model):
    uniqueid=models.IntegerField(max_length=50,default=0)
    transactionid=models.IntegerField(max_length=50,default=0)

def __str__(self):
    return str(self.process_pending_payment)
    