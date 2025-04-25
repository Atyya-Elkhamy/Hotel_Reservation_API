from django.urls import path
from .views import QueryAPIView, QueryHistoryAPIView

urlpatterns = [
    path('query/', QueryAPIView.as_view(), name='query'),
    path('history/', QueryHistoryAPIView.as_view(), name='query-history'),
]