from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from email.utils import formataddr
from twilio.rest import Client
from django.conf import settings
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import ListAPIView,CreateAPIView,UpdateAPIView,DestroyAPIView


# allowed for admins
class UserRegistrationView(CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return JsonResponse({"message": "User created successfully!", "user_id": user.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# allowed for admins
class UserDeleteView(DestroyAPIView):
    serializer_class = UserSerializer
    queryset = UserSerializer.Meta.model.objects.exclude(role='admin')

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
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
            if serializer.validated_data['role'] != 'customer' or serializer.validated_data['role'] != 'hotel_owner':
                return JsonResponse({"error": "Invalid role. Choose either 'customer' or 'hotel_owner'."}, status=400)
            else:
                user = serializer.save(role=serializer.validated_data['role'])
            return JsonResponse({"message": "User created successfully!", "user_id": user.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# allowed for anyone
class HotelOwnerAndCustomerUpdateView(UpdateAPIView):
    serializer_class = UserSerializer
    queryset = UserSerializer.Meta.model.objects.exclude(role__in=['admin', 'customer'])

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"message": "User updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


#allowed for hotel oweners
class EmployeeRegistraionView(CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save(role='hotel_staff')
            return JsonResponse({"message": "Employee created successfully!", "user_id": user.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# allowed for hotel owners
class EmployeeUpdateView(UpdateAPIView):
    serializer_class = UserSerializer
    queryset = UserSerializer.Meta.model.objects.filter(role='hotel_staff')

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return JsonResponse({"message": "Employee updated successfully!", "user_id": instance.id}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# allowed for hotel owners
class EmployeeDeleteView(DestroyAPIView):
    serializer_class = UserSerializer
    queryset = UserSerializer.Meta.model.objects.filter(role='hotel_staff')

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