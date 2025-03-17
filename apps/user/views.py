from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer, UserUpdateSerializer
from core.utils import success_response, error_response

User = get_user_model()


class UserRegisterView(APIView):
    """用户注册视图"""
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                
                return success_response(
                    data={
                        "user_id": str(user.id),
                        "username": user.username,
                        "token": {
                            "access": str(refresh.access_token),
                            "refresh": str(refresh)
                        }
                    },
                    message="注册成功",
                    code=201
                )
            except Exception as e:
                return error_response(message=f"注册失败: {str(e)}", code=400)
        
        # 格式化错误信息
        error_msg = ""
        for field, errors in serializer.errors.items():
            error_msg += f"{field}: {errors[0]} "
            
        return error_response(message=error_msg.strip(), code=400)


class LoginView(APIView):
    """用户登录视图"""

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return success_response(
                    data={
                        "access_token": str(refresh.access_token),
                        "refresh_token": str(refresh)
                    },
                    message="登录成功"
                )
            return error_response(message="用户名或密码错误", code=401)
        return error_response(message=serializer.errors, code=400)


class LogoutView(APIView):
    """用户登出视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 从请求体中获取刷新令牌
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return error_response(message="需要提供刷新令牌", code=400)
                
            # 将刷新令牌加入黑名单
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return success_response(
                data={"message": "已登出"},
                message="登出成功"
            )
        except TokenError as e:
            return error_response(message=f"令牌错误: {str(e)}", code=400)
        except Exception as e:
            return error_response(message=str(e), code=400)


class UserProfileView(APIView):
    """用户信息视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取用户信息"""
        serializer = UserProfileSerializer(request.user)
        return success_response(data=serializer.data)

    def put(self, request):
        """更新用户信息"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data={"user_id": request.user.id},
                message="更新成功"
            )
        return error_response(message=serializer.errors, code=400)
