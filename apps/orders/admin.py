from django.contrib import admin

from apps.orders.models import AccessTokens, AvailableRecharge, Orders, OrdersDetails, VerifiedAccounts

# Register your models here.


@admin.register(AccessTokens)
class AccessTokensAdmin(admin.ModelAdmin):
    list_display = ('id', 'valid_upto', "updated_at", )


@admin.register(AvailableRecharge)
class AvailableRechargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', "service_type", )


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', "service_type", "recharge_type", "status")


@admin.register(OrdersDetails)
class OrdersDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', "transaction_id",)


admin.site.register(VerifiedAccounts)
