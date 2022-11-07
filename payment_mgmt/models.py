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

class auth_token(models.Model):
    response=models.IntegerField(max_length=10,default='')
    status=models.CharField(max_length=100,default='')
    accessToken=models.BooleanField(max_length=100,default='')
    expiresIn=models.IntegerField(max_length=10,default='')
    tokenType=models.CharField(max_length=100,default='')
    walletBalance=models.IntegerField(max_length=100,default='')
    

    def __str__(self):
        return str(self.auth_token)

class balance_and_Payment(models.Model):
    status=models.CharField(max_length=100,default='')
    responsecode=models.IntegerField(max_length=100,default='')
    balance=models.IntegerField(max_length=100,default='')
    transaction_date=models.DateTimeField(auto_now_add=True)
    responsemessage=models.CharField(max_length=100,default='')

def __str__(self):
    return str(self.balance_and_Payment)

class merchant_transaction_report(models.Model):
    from_date=models.DateField()
    to_date=models.DateField()
    status=models.CharField(max_length=100,default='')
    responsecode=models.IntegerField(max_length=100,default='')
    balance=models.IntegerField(max_length=100,default='')
    responsemessage=models.CharField(max_length=100,default='')
    transaction_report=models.DateTimeField(auto_now_add=True)


def __str__(self):
    return str(self.merchant_transaction_report)

class merchant_pending_transaction(models.Model):
    from_date=models.DateField(max_length=10,default='')
    to_date=models.DateField(max_length=10,default='')
    status=models.CharField(max_length=100,default='')
    service_id=models.IntegerField(max_length=100,default='')
    transaction_id=models.AutoField(max_length=100,default='')
    transaction_amount=models.IntegerField(max_length=100,default='')
    unique_field=models.IntegerField(max_length=100,default='')
    
def __str__(self):
    return str(self.merchant_pending_transaction)



class merchant_check_status_transactionid(models.Model):
    status=models.CharField(max_length=100,default='')
    responsecode=models.IntegerField(max_length==100,default='')
    username=models.ForeignKey(Username, on_delete=models.CASCAD)
    biller_code=models.IntegerField(max_length=100,default='')
    provide_transactionid=models.IntegerField(max_length=100,default='')
    responsemessage=models.CharField(max_length=100,default='')

def __str__(self):
    return str(self.merchant_check_status_transactionid)

class repost_pending_transaction(models.Model):
    from_date=models.DurationField()
    to_date=models.DurationField()
    status=models.CharField(max_length=100,default='')
    unique_id=models.IntegerField(max_length=100,default='')
    transaction_id=models.IntegerField(max_length=100,default='')

def __str__(self):
    return str(self.repost_pending_transaction)

class merchant_balance_check(models.Model):
    status=models.CharField(max_length=100,default='')
    responsecode=models.IntegerField(max_length==100,default='')
    username=models.ForeignKey(Username, on_delete=models.CASCADE)
    balance=models.IntegerField(max_length=100,default='')
    responsemessage=models.CharField(max_length=100,default='')

def __str__(self):
    return str(self.merchant_balance_check)

class transaction_list(models.Model):
    status=models.CharField(max_length=100,default='')
    from_date=models.DateField(max_length=100,default='')
    to_date=models.DateField(max_length==100,default='')
    transaction_list=models.DateTimeField(auto_now_add=True)
    data=models.IntegerField(max_length=100,default='')

def __str__(self):
    return str(self.transaction_list)













