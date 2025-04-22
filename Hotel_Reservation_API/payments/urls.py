from django.urls import path
from .views import PaymentListCreateView, PaymentDetailView, PaymentForReservationCreateView, PaymentSettingsView

urlpatterns = [
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/create-for-reservation/', PaymentForReservationCreateView.as_view(), name='payment-create-for-reservation'),
    path('payment-settings/', PaymentSettingsView.as_view(), name='payment-settings'),
]
