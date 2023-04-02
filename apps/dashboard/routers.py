from django.urls import path

from rest_framework.routers import SimpleRouter

from apps.dashboard.views import DashboardAPIView

router = SimpleRouter()

# router.register(r'chat', ChatViewSet, basename='chat')


urlpatterns = [

    path('', DashboardAPIView.as_view(), name='dashboard'),

]

urlpatterns += router.urls