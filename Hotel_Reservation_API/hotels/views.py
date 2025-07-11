from django.shortcuts import render
from rest_framework import viewsets
from .models import Hotel, Room , HotelImage
from .serializers import HotelSerializer, RoomSerializer , HotelImageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from notifications.models import Notification
from rest_framework.generics import UpdateAPIView, ListAPIView, CreateAPIView, DestroyAPIView

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
    
# class HotelUpdateView(APIView):
#     def get_object(self, pk):
#         try:
#             return Hotel.objects.get(pk=pk)
#         except Hotel.DoesNotExist:
#             return None

#     def put(self, request, pk):
#         hotel = self.get_object(pk)
#         if hotel is None:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         serializer = HotelSerializer(hotel, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             Notification.objects.create(
#                 user=request.user,
#                 message="Your hotel has been successfully updated!"
#             )
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HotelUpdateView(UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    # permission_classes = [IsAuthenticated] 
    def perform_update(self, serializer):
        hotel = serializer.save()
        Notification.objects.create(
            user=self.request.user,
            message=f"Your hotel '{hotel.name}' has been successfully updated!"
        )





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
        Notification.objects.create(
            user=self.request.user,
            message=f"Your hotel '{hotel.name}' has been successfully deleted!"
        )
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

class HotelFilterByStarsView(APIView):
    def get(self, request, stars):
        hotels = Hotel.objects.filter(stars=stars)
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data)

class RoomCreateView(APIView):
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomListView(APIView):
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomFilterByTypeView(APIView):
    def get(self, request, room_type):
        rooms = Room.objects.filter(room_type=room_type)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)


class RoomUpdateView(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None

    def put(self, request, pk):
        room = self.get_object(pk)
        if room is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            Notification.objects.create(
                user=request.user,
                message=f"Room '{serializer.validated_data['room_type']}' has been successfully updated!"
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RoomDeleteView(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None

    def delete(self, request, pk):
        room = self.get_object(pk)
        if room is None:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        room.delete()
        Notification.objects.create(
            user=request.user,
            message=f"Room '{room.room_type}' has been successfully deleted!"
        )
        return Response({"message": "Room deleted"}, status=status.HTTP_204_NO_CONTENT)
    
class RoomDetailView(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_object(pk)
        if room is None:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoomSerializer(room)
        return Response(serializer.data)
    

class HotelImageCreateView(APIView):
    def post(self, request, pk):
        hotel = Hotel.objects.get(pk=pk)
        serializer = HotelImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hotel=hotel)
            Notification.objects.create(
                user=request.user,
                message=f"Image for hotel '{hotel.name}' has been successfully created!"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class HotelImageListView(APIView):
    def get(self, request, pk):
        hotel = Hotel.objects.get(pk=pk)
        images = hotel.images.all()
        serializer = HotelImageSerializer(images, many=True)
        return Response(serializer.data)
class HotelImageUpdateView(APIView):
    def get_object(self, pk):
        try:
            return HotelImage.objects.get(pk=pk)
        except HotelImage.DoesNotExist:
            return None

    def put(self, request, pk):
        hotel_image = self.get_object(pk)
        if hotel_image is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HotelImageSerializer(hotel_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            Notification.objects.create(
                user=request.user,
                message=f"Image for hotel '{hotel_image.hotel.name}' has been successfully updated!"
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class HotelImageDeleteView(APIView):
    def get_object(self, pk):
        try:
            return HotelImage.objects.get(pk=pk)
        except HotelImage.DoesNotExist:
            return None

    def delete(self, request, pk):
        hotel_image = self.get_object(pk)
        if hotel_image is None:
            return Response({"error": "Hotel image not found"}, status=status.HTTP_404_NOT_FOUND)
        hotel_image.delete()
        Notification.objects.create(
            user=request.user,
            message=f"Image for hotel '{hotel_image.hotel.name}' has been successfully deleted!"
        )
        return Response({"message": "Hotel image deleted"}, status=status.HTTP_204_NO_CONTENT)
