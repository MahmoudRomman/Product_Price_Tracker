from django.urls import path
from .views import register_user, UserProfileView

urlpatterns = [
    path('users/register/', register_user, name='register'),
    path('users/me/', UserProfileView.as_view(), name='user_profile'),
]