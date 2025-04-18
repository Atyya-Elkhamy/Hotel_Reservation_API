from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from email.utils import formataddr
from twilio.rest import Client
from django.conf import settings
from .serializers import UserSerializer
from rest_framework.generics import CreateAPIView
# from rest_framework.decorators import api_view

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