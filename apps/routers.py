from django.conf.urls import include, url

urlpatterns = [
    url("payment/", include('apps.payment.routers')),
    url("orders/", include('apps.orders.routers')),
    url("cms/", include('apps.cms.routers')),
    url("notification/", include('apps.notification.routers')),
    url("sub-admin/", include('apps.sub_admin.routers')),
    url("issues/", include('apps.issues.routers')),
    url("reports/", include('apps.reports.routers')),
    url("chat/", include('apps.chat.routers')),
    url("dashboard/", include('apps.dashboard.routers')),

]
