from rest_framework.views import APIView 
from rest_framework.generics import ListAPIView ,RetrieveAPIView
from rest_framework.permissions import IsAuthenticated 
from accounts.permissions import IsHotelOwner
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, BookingCartItem, BookingCartSummary
from .serializers import *
from hotels.models import RoomType
from django.shortcuts import get_object_or_404

class CreateBookingView(APIView):
    def post(self, request):
        print("Request Data:", request.data)
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response({
                "message": "Booking created successfully.",
                "booking_id": booking.id,
                "hotel": booking.hotel.name,
                "check_in": booking.check_in,
                "days": booking.days,
                "total_price": booking.total_price,
                "created_items": [
                    {
                        "room_type": item.room_type.room_type,
                        "quantity": item.quantity
                    } for item in booking.items.all()
                ],
                "summary_created": True
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

class BookingPaymentDetailView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if not hasattr(booking, "cart_summary"):
            return Response({"detail": "Summary not found. Please generate summary first."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = BookingPaymentSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingListAPIView(ListAPIView):
    serializer_class = ListBookingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all bookings for the authenticated user
        return Booking.objects.all()


class BookingListAPIView(ListAPIView):
    serializer_class = ListBookingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all bookings for the authenticated user
        return Booking.objects.filter(user=self.request.user.id)

class BookingListByHotelAPIView(ListAPIView):
    serializer_class = ListBookingsSerializer
    permission_classes = [IsAuthenticated, IsHotelOwner]

    def get_queryset(self):
        hotel_owner = self.request.user.id
        hotel = Hotel.objects.filter(owner=hotel_owner).first()
        if hotel:
            return Booking.objects.filter(hotel=hotel)
        else:
            return NotFound("Hotel Has no reservations yet.")
        

class BookingsPaymentAllView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingPaymentSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HotelOwnerBookingsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # Use the authenticated user instead of passing owner_id
        owner = request.user

        # Get all hotels owned by the user
        hotels = Hotel.objects.filter(owner=owner)
        
        if not hotels:
            return Response({"detail": "No hotels found for this owner."}, status=404)

        flat_booking_data = []
        
        # Iterate over all hotels
        for hotel in hotels:
            # Get all bookings for the hotel
            bookings = Booking.objects.filter(hotel=hotel)

            # Iterate over bookings and add each one to the flat list
            for booking in bookings:
                # Serialize each booking with hotel info included
                booking_data = CustomBookingSerializer(booking).data
                # Add the hotel name and owner name to each booking
                booking_data["hotel_name"] = hotel.name
                booking_data["owner_name"] = hotel.owner.username  # Or use full name if preferred
                flat_booking_data.append(booking_data)

        return Response(flat_booking_data)
