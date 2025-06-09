from django.urls import path
from .views import CheckUserExistsView
app_name ="user_app"

urlpatterns =[
    path('check/', CheckUserExistsView.as_view(), name='check')
]