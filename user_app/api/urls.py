from django.urls import path
from .views import CheckUserExistsView, RegisterView, ActivateUserView, CookieTokenObtainPairView, CookieTokenRefreshView, ForgotPasswordView, ChangePasswordView


app_name ="user_app"

urlpatterns =[
    path('check/', CheckUserExistsView.as_view(), name='check'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateUserView.as_view(), name='activate'),
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('resetpassword/', ChangePasswordView.as_view(), name='password-reset'),
]