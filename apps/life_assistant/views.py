# 生活助手模块视图 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .tasks import fetch_weather_data, track_express_package, sync_dormitory_tasks
from core.utils import success_response, error_response
from django.core.cache import cache
import json

class WeatherView(APIView):
    """获取天气信息视图"""
    def get(self, request):
        location = request.query_params.get('location', '北京')
        
        # 尝试从缓存获取天气数据
        cache_key = f"weather_{location}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            # 如果缓存中有数据，直接返回
            return success_response(data=json.loads(cached_data))
        
        # 没有缓存，异步获取天气数据
        task = fetch_weather_data.delay(location)
        
        # 返回任务ID，前端可以使用轮询或WebSocket获取结果
        return success_response(
            data={"task_id": task.id, "status": "processing"},
            message="天气数据更新中，请稍后查询"
        )

class ExpressTrackView(APIView):
    """跟踪校园快递视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        tracking_number = request.data.get('tracking_number')
        express_company = request.data.get('express_company')
        
        if not tracking_number:
            return error_response(message="请提供快递单号", code=400)
        
        # 异步跟踪快递
        task = track_express_package.delay(tracking_number, express_company)
        
        return success_response(
            data={"task_id": task.id, "status": "processing"},
            message="正在获取快递信息，请稍后查询"
        )

class DormitoryTasksView(APIView):
    """宿舍待办事项管理视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        task_data = request.data.get('task')
        
        # 添加待办事项逻辑
        # ...
        
        # 异步同步待办事项到其他平台
        sync_dormitory_tasks.delay(request.user.id, task_data)
        
        return success_response(
            data={"status": "success"},
            message="待办事项已添加"
        )
    
    def get(self, request):
        # 获取待办事项列表逻辑
        # ...
        
        # 模拟数据
        tasks = [
            {"id": 1, "title": "打扫宿舍", "status": "进行中"},
            {"id": 2, "title": "倒垃圾", "status": "已完成"}
        ]
        
        return success_response(data={"tasks": tasks}) 