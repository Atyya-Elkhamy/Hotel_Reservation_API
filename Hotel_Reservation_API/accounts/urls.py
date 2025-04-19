from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/', HotelOwnerAndCustomerRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('employee-register/', EmployeeRegistraionView.as_view(), name='employee-register'),
    path('employee-delete/<int:pk>/', EmployeeDeleteView.as_view(), name='employee-delete'),
    path('admin-register/', UserRegistrationView.as_view(), name='admin-register'),
    path('user-delete/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
    path('send-email/', send_test_email, name='send-email'),
]
