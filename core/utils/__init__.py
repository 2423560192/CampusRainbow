"""
Core utilities package.
"""

from rest_framework.response import Response
from core.utils.celery_utils import get_task_result

def success_response(data=None, message="请求成功", code=200):
    """
    标准成功响应
    """
    return Response({
        "status": "success",
        "code": code,
        "message": message,
        "data": data or {}
    }, status=code)

def error_response(message="请求失败", code=400):
    """
    标准错误响应
    """
    return Response({
        "status": "error",
        "code": code,
        "message": message
    }, status=code) 