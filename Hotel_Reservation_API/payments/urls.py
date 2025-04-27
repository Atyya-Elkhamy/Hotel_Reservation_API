from django.urls import path
from .views import ClientInfoPaymentTypeView,PaymentMethodSelectionView
urlpatterns = [
        path('client-info/', ClientInfoPaymentTypeView.as_view(), name='client-info'),
        path('payment-method/', PaymentMethodSelectionView.as_view(), name='payment-method'),
]
