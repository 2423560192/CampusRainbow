from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # 用户注册
    path('register', views.UserRegisterView.as_view(), name='register'),
    # 用户登录
    path('login', views.LoginView.as_view(), name='login'),
    # 用户登出
    path('logout', views.LogoutView.as_view(), name='logout'),
    # 用户信息
    path('profile', views.UserProfileView.as_view(), name='profile'),
    # 刷新token
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]