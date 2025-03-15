# 虚拟自习室模块路由
from django.urls import path
from . import views

urlpatterns = [
    # 加入自习室
    path('study_rooms/join/', views.JoinStudyRoomView.as_view(), name='join_study_room'),
    # 上传学习记录到区块链
    path('study_records/upload/', views.UploadStudyRecordView.as_view(), name='upload_study_record'),
    # AI 主持自习室
    path('ai/host_study/', views.AIHostStudyView.as_view(), name='ai_host_study'),
] 