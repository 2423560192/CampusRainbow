# 个人提升模块路由
from django.urls import path
from .views import (
    TaskListCreateView, TaskDetailView, TaskStartView, TaskPauseView,
    AIGeneratePlanView, AIAnalyzePlanView, FragmentTaskView,
    ResourceRecommendView, ResourceFavoriteView,
    EmotionAnalyzeView, EmotionHistoryView, VoiceAssistantView,
    AutoTaskView, AutoTaskCancelView
)

urlpatterns = [
    # 任务管理 API
    path('tasks', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<str:task_id>', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<str:task_id>/start', TaskStartView.as_view(), name='task-start'),
    path('tasks/<str:task_id>/pause', TaskPauseView.as_view(), name='task-pause'),
    
    # AI 计划 API
    path('ai/generate_plan', AIGeneratePlanView.as_view(), name='ai-generate-plan'),
    path('ai/analyze_plan', AIAnalyzePlanView.as_view(), name='ai-analyze-plan'),
    
    # 任务处理 API
    path('tasks/fragment', FragmentTaskView.as_view(), name='task-fragment'),
    
    # 资源管理 API
    path('resources/recommend', ResourceRecommendView.as_view(), name='resource-recommend'),
    path('resources/<str:resource_id>/favorite', ResourceFavoriteView.as_view(), name='resource-favorite'),
    
    # 情绪分析 API
    path('emotions/analyze', EmotionAnalyzeView.as_view(), name='emotion-analyze'),
    path('emotions/history', EmotionHistoryView.as_view(), name='emotion-history'),
    
    # 语音助手 API
    path('voice/assistant', VoiceAssistantView.as_view(), name='voice-assistant'),
    
    # 自动化任务 API
    path('tasks/auto_execute', AutoTaskView.as_view(), name='auto-task-create'),
    path('tasks/auto_execute/<str:task_id>/cancel', AutoTaskCancelView.as_view(), name='auto-task-cancel'),
]
