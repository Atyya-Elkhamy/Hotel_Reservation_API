from django.urls import path , include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    #admin views 
    path('user/', UserListCreateView.as_view(), name='user-list'),
    path('user/admin/',UserRetriveUpdateView.as_view(), name='user-admin'),
    path('user/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    #customer and hotel owner views
    path('user/register/', HotelOwnerAndCustomerRegistrationView.as_view(), name='register'),
    path('user/data', HotelOwnerAndCustomerRetriveUpdateView.as_view(), name='update'),
    #Hotel Owner views (for hotel staff)
    path('user/employee/',EmployeeListCreateview.as_view(), name='employee-list'),
    path('user/employee/<int:pk>/', EmployeeRetrieveUpdateDestroyView.as_view(), name='employee-detail'),
    #login, refresh token, and logout (blacklisting) views 
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path("register/",RegisterUser.as_view(),name="register_new_user"),
]
