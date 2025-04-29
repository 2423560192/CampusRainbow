from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .utils.celery_utils import get_task_result, get_cached_task_result
from celery.result import AsyncResult

class TaskStatusView(APIView):
    """
    任务状态查询视图
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        """
        获取任务状态和结果
        """
        # 首先尝试从缓存获取结果
        cached_result = get_cached_task_result(task_id)
        if cached_result:
            return Response({
                "task_id": task_id,
                "status": "SUCCESS",
                "result": cached_result,
                "source": "cache"
            })
        
        # 如果缓存中没有，则查询Celery
        task_result = get_task_result(task_id)
        
        return Response(task_result) 