from django.urls import path
from .views import *

urlpatterns = [
    path('send-email/', SendConfirmEmailAPIView.as_view(), name='send-confirm-email'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/mark-read/<int:pk>/', MarkNotificationAsReadView.as_view(), name='mark-notification-as-read'),
    path('notifications/delete/<int:pk>/', DeleteNotificationView.as_view(), name='delete-notification'),
]