# 认证模块视图 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class RegisterView(APIView):
    """用户注册视图"""
    def post(self, request):
        # 用户注册逻辑
        pass

class LoginView(APIView):
    """用户登录视图"""
    def post(self, request):
        # 用户登录逻辑
        pass

class LogoutView(APIView):
    """用户登出视图"""
    def post(self, request):
        # 用户登出逻辑
        pass 