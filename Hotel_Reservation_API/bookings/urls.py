from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('booking/payment/<int:booking_id>/', BookingPaymentDetailView.as_view(), name='booking-payment-detail'),
]
