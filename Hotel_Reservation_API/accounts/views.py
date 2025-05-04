from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from email.utils import formataddr
from twilio.rest import Client
from django.conf import settings
from .serializers import *
from .permissions import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView,RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response

# allowed for admins
class UserListCreateView(ListCreateAPIView): 
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    queryset = UserSerializer.Meta.model.objects.all()
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# allowed for admins
class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):  
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    queryset = UserSerializer.Meta.model.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return JsonResponse(serializer.data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"message": "User updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.role == 'admin':
                return JsonResponse({"error": "Cannot delete admin user."}, status=400)
            self.perform_destroy(instance)
            return JsonResponse({"message": "User deleted successfully!"}, status=204)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class UserRetriveUpdateView(RetrieveUpdateAPIView): 
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        return self.request.user
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response (serializer.data)
        except Exception as e:
            print("GET error:", str(e))
            return JsonResponse({"error": str(e)}, status=400)
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"message": "User updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
            print(e,'line 100 from UserRetriveUpdateView')
            return JsonResponse({"error": str(e)}, status=400)

# allowed for anyone
class HotelOwnerAndCustomerRegistrationView(CreateAPIView):
    serializer_class = UserSerializer
    def create(self, request, *args, **kwargs):
        serilizer = UserSerializer(data=request.data)
        if serilizer.is_valid():
            role = 'customer'
            serilizer.save(role=role)
            return Response(serilizer.data,status=status.HTTP_201_CREATED)
        return Response(serilizer.errors,status=status.HTTP_400_BAD_REQUEST)

class HotelOwnerAndCustomerRetriveUpdateView(RetrieveUpdateAPIView): 
    serializer_class = UserSerializer
    permission_classes = [IsHotelOwner | IsCustomer]
    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response (serializer.data)
        except Exception as e:
            print("GET error:", str(e))  # ← this will help
            return JsonResponse({"error": str(e)}, status=400)
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"message": "User updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=400)
        
#allowed for hotel oweners
class EmployeeListCreateview(ListCreateAPIView): 
    serializer_class = UserSerializer
    permission_classes = [IsHotelOwner]
    queryset = UserSerializer.Meta.model.objects.filter(role='hotel_staff')

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save(role='hotel_staff')
            return JsonResponse({"message": "Employee created successfully!", "user_id": user.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# allowed for hotel owners
class EmployeeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView): 
    serializer_class = UserSerializer
    permission_classes = [IsHotelOwner]
    queryset = UserSerializer.Meta.model.objects.filter(role='hotel_staff')

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return JsonResponse(serializer.data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"message": "Employee updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return JsonResponse({"message": "Employee deleted successfully!"}, status=204)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# login view
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#logout view
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return JsonResponse({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RegisterUser(APIView):
    def post(self , request):
        serilizer = UserSerializerCreate(data=request.data)
        if serilizer.is_valid():
            role = 'customer'
            serilizer.save(role=role)
            return Response(serilizer.data,status=status.HTTP_201_CREATED)
        return Response(serilizer.errors,status=status.HTTP_400_BAD_REQUEST)