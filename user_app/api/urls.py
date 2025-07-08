from django.urls import path
from .views import CheckUserExistsView, LogInView, RegisterView, ActivateUserView, CookieTokenObtainPairView, CookieTokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name ="user_app"

urlpatterns =[
    path('check/', CheckUserExistsView.as_view(), name='check'),
    path('login/', LogInView.as_view(), name='login'),
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateUserView.as_view(), name='activate')
]