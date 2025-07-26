from django.urls import path
from .views import CheckUserExistsView, RegisterView, ActivateUserView, CookieTokenObtainPairView, CookieTokenRefreshView, ForgotPasswordView, ChangePasswordView, CookieTokenRemoveView


app_name ="user_app"

urlpatterns =[
    path('check/', CheckUserExistsView.as_view(), name='check'),
    path('login/', CookieTokenObtainPairView.as_view(), name='login'),
    path('logout/', CookieTokenRemoveView.as_view(), name='logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('password_reset/', ForgotPasswordView.as_view(), name='password-reset'),
    path('password_confirm/<uidb64>/<token>/', ChangePasswordView.as_view(), name='password-confirm'),
]