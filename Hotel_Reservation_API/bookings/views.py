from rest_framework.views import APIView
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
            return Response({
                "message": "Booking creation failed.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class BookingPaymentDetailView(APIView):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if not hasattr(booking, "cart_summary"):
            return Response({"detail": "Summary not found. Please generate summary first."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = BookingPaymentSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class BookingPaymentDetailView(APIView):
#     def get(self, request, user_id):
#         if request.user.id != user_id:
#             return Response(
#                 {"detail": "You do not have permission to view this user's bookings."},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         booking = Booking.objects.filter(user_id=user_id).order_by('-created_at').first()
#         if not booking:
#             return Response(
#                 {"detail": "No booking found for this user."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         if not hasattr(booking, "cart_summary"):
#             return Response(
#                 {"detail": "Summary not found. Please generate summary first."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         serializer = BookingPaymentSerializer(booking)
#         return Response(serializer.data, status=status.HTTP_200_OK)
