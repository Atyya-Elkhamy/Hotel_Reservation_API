from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from email.utils import formataddr
from twilio.rest import Client
from django.conf import settings
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .permissions import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView,RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework import status, permissions



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
            user = serializer.save()
            return JsonResponse({"message": "User created successfully!", "user_id": user.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


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

# allowed for anyone
class HotelOwnerAndCustomerRegistrationView(CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            role = serializer.validated_data['role']
            confirmed = serializer.validated_data.get('confirmed')
            if role not in ['customer', 'hotel_owner']:
                return JsonResponse({"error": "Invalid role. Choose either 'customer' or 'hotel_owner'."}, status=400)
            elif confirmed:
                return JsonResponse({"error": "Provided Unknown credentials 'confirmed' "}, status=400)
            else:
                user = serializer.save(role=serializer.validated_data['role'])
            return JsonResponse({"message": "User created successfully!", "user_id": user.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class HotelOwnerAndCustomerRetriveUpdateView(RetrieveUpdateAPIView): 
    serializer_class = UserSerializer
    permission_classes = [IsHotelOwner | IsCustomer]

    def get_object(self):
        return self.request.user

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
            confirmed = serializer.validated_data.get['confirmed']
            if confirmed:
                return JsonResponse({"error": "Provided Unknown credentials 'confirmed' "}, status=400)
            else:
                serializer.save()
            return JsonResponse({"message": "User updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
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



def send_test_email(request):
    try:
        send_mail(
            subject='Hello from Django!',
            message='This is a test email 💌',
            from_email=formataddr(("Hotel_App", "atyyaelkhamy50@gmail.com")),
            recipient_list=['atiaelkhamy55@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {e}", status=500)
