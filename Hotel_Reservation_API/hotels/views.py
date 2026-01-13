from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, ListAPIView
from .models import Hotel, Room, HotelImage, RoomType
from .serializers import *
from notifications.models import Notification
from rest_framework.permissions import IsAuthenticated , AllowAny
from accounts.permissions import IsHotelOwner

class HotelListView(APIView):
    def get(self, request):
        hotels = Hotel.objects.all()
        serializer = HotelSerializer(hotels, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HotelSerializerCreate(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class HotelUpdateView(UpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    def perform_update(self, serializer):
        serializer.save()   

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
    def get(self, request, pk):
        try:
            hotel = Hotel.objects.get(pk=pk)
        except Hotel.DoesNotExist:
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
        if 'room_type' in request.data:
            try:
                room_type_id = request.data['room_type']
                room_type = RoomType.objects.get(id=room_type_id)
                request.data['room_type'] = room_type.id  
            except RoomType.DoesNotExist:
                return Response({"error": "RoomType does not exist"}, status=status.HTTP_400_BAD_REQUEST)
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
        return Response({"message": "Room deleted"}, status=status.HTTP_204_NO_CONTENT)

class RoomDetailView(APIView):
    def get(self, request, pk):
        try:
            room = Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoomSerializerFetch(room)
        return Response(serializer.data)
class RoomsByHotelView(APIView):
    def get(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(pk=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

        rooms = Room.objects.filter(hotel=hotel)
        serializer = RoomSerializer(rooms, many=True)
        print(serializer.data)
        return Response(serializer.data)
#room type views
class RoomTypeView(APIView):
    def post(self, request):
        try:
            hotel = Hotel.objects.get(pk=request.data['hotel'])
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoomTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hotel=hotel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HotelsRoomTypeView(APIView):
    def get(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(pk=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

        room_types = RoomType.objects.filter(hotel=hotel)
        serializer = RoomTypeSerializer(room_types, many=True)
        return Response(serializer.data)
    
# Hotel Image Views
class HotelImageCreateView(APIView):
    def post(self, request, *args, **kwargs):
        hotel_id = request.data.get('hotel_id')
        if not hotel_id:
            return Response({"error": "Hotel ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HotelImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hotel=hotel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HotelImageListView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                hotel = Hotel.objects.get(pk=pk)
                images = hotel.images.all()
            except Hotel.DoesNotExist:
                return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            images = HotelImage.objects.all()
        
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
        return Response({"message": "Hotel image deleted"}, status=status.HTTP_204_NO_CONTENT)
# Room Image Views      

class RoomImageCreateView(APIView):
    def post(self, request):
        try:
            room = Room.objects.get(pk=request.data['room'])
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoomImageSerializerAdd(data=request.data)
        if serializer.is_valid():
            serializer.save(room=room)
            Notification.objects.create(
                user=request.user,
                message=f"Image for room '{room.room_type}' has been successfully created!"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RoomImageListView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                room = Room.objects.get(pk=pk)
                images = room.images.all()
            except Room.DoesNotExist:
                return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            images = HotelImage.objects.all()
        serializer = HotelImageSerializer(images, many=True)
        return Response(serializer.data)
    
class RoomImageUpdateView(APIView):
    def get_object(self, pk):
        try:
            return HotelImage.objects.get(pk=pk)
        except HotelImage.DoesNotExist:
            return None
    def put(self, request, pk):
        room_image = self.get_object(pk)
        if room_image is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HotelImageSerializer(room_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            Notification.objects.create(
                user=request.user,
                message=f"Image for room '{room_image.room.room_type}' has been successfully updated!"
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RoomImageDeleteView(APIView): 
    def get_object(self, pk):
        try:
            return RoomImage.objects.get(pk=pk)
        except RoomImage.DoesNotExist:
            return None
    def delete(self, request, pk):
        room_image = self.get_object(pk)
        if room_image is None:
            return Response({"error": "Room image not found"}, status=status.HTTP_404_NOT_FOUND)
        room_image.delete()
        return Response({"message": "Room image deleted"}, status=status.HTTP_204_NO_CONTENT)

class OwnerHotelListView(ListAPIView):
    serializer_class = HotelSerializer
    def get_queryset(self):
        user = self.request.user.id
        print(user , "this is the user id")
        return Hotel.objects.filter(owner=user)