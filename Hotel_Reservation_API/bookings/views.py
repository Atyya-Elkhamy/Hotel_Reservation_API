from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer, ListBookingsSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveAPIView,ListAPIView


class BookingListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.user != request.user:
            raise PermissionDenied("You do not have permission to view this booking.")
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.user != request.user:
            raise PermissionDenied("You do not have permission to view this booking.")
        serializer = BookingSerializer(instance=booking, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        if booking.user != request.user:
            raise PermissionDenied("You do not have permission to view this booking.")
        booking.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class BookingListAPIView(ListAPIView):
    serializer_class = ListBookingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get all bookings for the authenticated user
        return Booking.objects.filter(user=self.request.user.id)