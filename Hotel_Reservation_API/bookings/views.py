from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny


class BookingListCreateAPIView(APIView):
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request):
        #bookings = Booking.objects.filter(user=request.user)
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailAPIView(APIView):
    #permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        # if booking.user != request.user:
        #     raise PermissionDenied("You do not have permission to view this booking.")
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        # if booking.user != request.user:
        #     raise PermissionDenied("You do not have permission to view this booking.")
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        # if booking.user != request.user:
        #     raise PermissionDenied("You do not have permission to view this booking.")
        booking.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
