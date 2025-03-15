# 个人提升模块路由
from django.urls import path
from . import views

urlpatterns = [
    # 创建新的学习计划
    path('plans/', views.PlanCreateView.as_view(), name='create_plan'),
    # 获取指定计划的详情
    path('plans/<str:plan_id>/', views.PlanDetailView.as_view(), name='plan_detail'),
    # AI 生成学习计划
    path('ai/generate_plan/', views.AIGeneratePlanView.as_view(), name='ai_generate_plan'),
    # 碎片化任务拆解
    path('tasks/fragment/', views.TaskFragmentView.as_view(), name='task_fragment'),
    # 自动推荐学习资源
    path('resources/recommend/', views.ResourceRecommendView.as_view(), name='resource_recommend'),
    # 学习情绪分析与调节建议
    path('emotions/analyze/', views.EmotionAnalyzeView.as_view(), name='emotion_analyze'),
    # 语音助手控制任务
    path('voice/assistant/', views.VoiceAssistantView.as_view(), name='voice_assistant'),
    # 设置自动执行任务
    path('tasks/auto_execute/', views.AutoExecuteTaskView.as_view(), name='auto_execute_task'),
] 