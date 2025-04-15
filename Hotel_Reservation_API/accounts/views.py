from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from email.utils import formataddr
from twilio.rest import Client
from django.conf import settings


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