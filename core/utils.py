from rest_framework.views import exception_handler
from rest_framework.response import Response

# Import and re-export the get_task_result function
from .utils.celery_utils import get_task_result

def custom_exception_handler(exc, context):
    """
    自定义异常处理器，确保所有响应格式一致
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            'status': 'error',
            'code': response.status_code,
            'message': str(exc),
        }
        response.data = error_data
    
    return response

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