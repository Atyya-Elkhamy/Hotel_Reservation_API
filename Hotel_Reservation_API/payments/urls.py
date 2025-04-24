from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentSettingsViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-settings', PaymentSettingsViewSet, basename='payment-settings')

urlpatterns = [
    path('', include(router.urls)),
]
