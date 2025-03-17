from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'phone')
        extra_kwargs = {
            'password': {'write_only': True},
            'phone': {'required': False}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        if 'phone' in validated_data:
            user.phone = validated_data['phone']
            user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    user_id = serializers.CharField(source='id', read_only=True)

    class Meta:
        model = User
        fields = (
            'user_id', 'username', 'email', 'phone', 'avatar', 'bio',
            'is_verified', 'student_id', 'university', 'major', 'grade',
            'total_focus_time', 'total_savings'
        )
        read_only_fields = ('user_id', 'username', 'is_verified', 'total_focus_time', 'total_savings')


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""

    class Meta:
        model = User
        fields = (
            'email', 'phone', 'avatar', 'bio',
            'student_id', 'university', 'major', 'grade'
        )
        extra_kwargs = {
            'email': {'required': False},
            'phone': {'required': False},
            'avatar': {'required': False},
            'bio': {'required': False},
            'student_id': {'required': False},
            'university': {'required': False},
            'major': {'required': False},
            'grade': {'required': False}
        }
