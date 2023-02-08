from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(PaymentTransactions)
admin.site.register(StripeCustomer)
admin.site.register(PaymentMethods)



