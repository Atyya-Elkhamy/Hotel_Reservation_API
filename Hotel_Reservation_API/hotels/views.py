from django.shortcuts import render
from rest_framework import viewsets
from .models import Hotel, Room
from .serializers import HotelSerializer, RoomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HotelListView(APIView):
    def get(self, request):
        hotels = Hotel.objects.all()
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = HotelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HotelUpdateView(APIView):
    def get_object(self, pk):
        try:
            return Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            return None

    def put(self, request, pk):
        hotel = self.get_object(pk)
        if hotel is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HotelSerializer(hotel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HotelDeleteView(APIView):
    def get_object(self, pk):
        try:
            return Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            return None

    def delete(self, request, pk):
        hotel = self.get_object(pk)
        if hotel is None:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        hotel.delete()
        return Response({"message": "Hotel deleted"}, status=status.HTTP_204_NO_CONTENT)
    

class HotelDetailView(APIView):
    def get_object(self, pk):
        try:
            return Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
            return None

    def get(self, request, pk):
        hotel = self.get_object(pk)
        if hotel is None:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = HotelSerializer(hotel)
        return Response(serializer.data)
