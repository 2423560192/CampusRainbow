# 虚拟自习室模块视图 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .tasks import process_join_study_room, upload_to_blockchain, ai_host_study_session
from core.utils import success_response, error_response

class JoinStudyRoomView(APIView):
    """加入自习室视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        room_id = request.data.get('room_id')
        
        if not room_id:
            return error_response(message="请提供自习室ID", code=400)
        
        # 异步处理加入自习室请求
        task = process_join_study_room.delay(request.user.id, room_id)
        
        return success_response(
            data={"task_id": task.id, "status": "processing"},
            message="正在处理加入自习室请求"
        )

class UploadStudyRecordView(APIView):
    """上传学习记录到区块链视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        study_record = request.data.get('study_record')
        
        if not study_record:
            return error_response(message="请提供学习记录", code=400)
        
        # 异步上传学习记录到区块链
        task = upload_to_blockchain.delay(request.user.id, study_record)
        
        return success_response(
            data={"task_id": task.id, "status": "processing"},
            message="正在上传学习记录到区块链"
        )

class AIHostStudyView(APIView):
    """AI 主持自习室视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        room_id = request.data.get('room_id')
        session_config = request.data.get('config', {})
        
        if not room_id:
            return error_response(message="请提供自习室ID", code=400)
        
        # 异步启动AI主持会话
        task = ai_host_study_session.delay(room_id, session_config)
        
        return success_response(
            data={"task_id": task.id, "status": "processing"},
            message="AI正在启动自习室会话"
        ) 