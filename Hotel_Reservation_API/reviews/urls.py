from django.urls import path
from . import views

urlpatterns = [
    path('getall/', views.ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path('create/', views.ReviewListCreateAPIView.as_view(), name='review-list-create'),
    path('details/<int:pk>/', views.ReviewDetailAPIView.as_view(), name='review-detail'),
    path('hotels/<int:hotel_id>/reviews/', views.HotelReviewsAPIView.as_view(), name='hotel-reviews'),
]