from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name="signup"),
    path('login/', views.LoginView.as_view(), name="login"),
    path("jwt/create/", TokenObtainPairView.as_view(), name="jwt_create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh_token"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt_verify_token"),
    path('update-user/', views.UpdateUserView.as_view(), name='user-update'),
    path('delete-user/', views.DeleteUserView.as_view(), name='user-update'),
]
