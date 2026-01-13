from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CreateBookingView.as_view(), name='create-booking'),
    path('booking/payment/<int:booking_id>/', BookingPaymentDetailView.as_view(), name='booking-payment-detail'),
    path('', BookingListAPIView.as_view(), name='booking-list'),
    path('allbookingsandpaments/',BookingsPaymentAllView.as_view(), name='all-bookings-and-payments'), 
    path('userbookings/', BookingListAPIView.as_view(), name='user-booking-detail'),
    path('hotelbookings/', BookingListByHotelAPIView.as_view(), name='hotel-booking-detail'),
    path('owner/hotels/', HotelOwnerBookingsView.as_view(), name='owner-hotels'),
]
