from django.urls import path
from .views import CheckUserExistsView, LogInView, RegisterView
app_name ="user_app"

urlpatterns =[
    path('check/', CheckUserExistsView.as_view(), name='check'),
    path('login/', LogInView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
]