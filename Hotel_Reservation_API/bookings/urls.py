from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('booking/payment/<int:booking_id>/', BookingPaymentDetailView.as_view(), name='booking-payment-detail'),
    # path('', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    # path('<int:pk>/', BookingDetailAPIView.as_view(), name='booking-detail'),
    path('', BookingListAPIView.as_view(), name='booking-list'),
    path('userbookings/', BookingRetrieveAPIView.as_view(), name='user-booking-detail'),
    path('hotelbookings/', BookingListByHotelAPIView.as_view(), name='hotel-booking-detail'),
]
