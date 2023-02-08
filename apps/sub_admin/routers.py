from django.urls import re_path, path

from rest_framework.routers import SimpleRouter

from apps.sub_admin.views import CountryViewSet, CityViewSet

router = SimpleRouter()

router.register(r'country', CountryViewSet, basename='country')
router.register(r'city', CityViewSet, basename='city')


urlpatterns = [
    # path('stripe/initiate', StripePaymentAPIView.as_view(), name='stripe-initiate-payment'),
]

urlpatterns += router.urls
