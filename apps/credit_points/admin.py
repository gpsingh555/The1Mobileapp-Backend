from django.contrib import admin

from apps.credit_points.models import UserCreditPoint, CreditPointTransaction

# Register your models here.

admin.site.register(UserCreditPoint)
admin.site.register(CreditPointTransaction)