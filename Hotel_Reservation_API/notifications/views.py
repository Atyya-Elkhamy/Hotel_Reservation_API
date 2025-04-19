from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from email.utils import formataddr
from twilio.rest import Client
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import *
from rest_framework import status


# def send_test_email(request):
#     try:
#         recever_email = request.GET.get('email')
#         message = request.GET.get('message')
#         send_mail(
#             subject='Hello from Django!',
#             message=message,
#             from_email=formataddr(("Hotel_App", "atyyaelkhamy50@gmail.com")),
#             recipient_list=recever_email,
#             fail_silently=False,
#         )
#         return HttpResponse("Email sent successfully!")
#     except Exception as e:
#         return HttpResponse(f"Failed to send email: {e}", status=500)
    
class SendConfirmEmailAPIView(APIView):
    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            message = serializer.validated_data['message']
            try:
                send_mail(
                    subject='Hello from Django!',
                    message=message,
                    from_email=formataddr(("Hotel_App", "atyyaelkhamy50@gmail.com")),
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response({'message': 'Email sent successfully!'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': f'Failed to send email: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationListView(APIView):
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(user=user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkNotificationAsReadView(APIView):
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        
class DeleteNotificationView(APIView):
    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete()
            return Response({"message": "Notification deleted"})
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)



