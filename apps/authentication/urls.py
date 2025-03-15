# 认证模块路由
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),
    # 用户登录
    path('login/', views.LoginView.as_view(), name='login'),
    # 用户登出
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # 刷新token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 