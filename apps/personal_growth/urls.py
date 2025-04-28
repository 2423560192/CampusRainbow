# 个人提升模块路由
from django.urls import path
from .views import (
    PlanCreateView, PlanDetailView, PlanPauseResumeView, PlanStartView,
    EmotionHistoryView, EmotionAnalysisView,
    VoiceAssistantView, AIGeneratePlanView, AIPlanDetailView, AIAnalyzePlanView,
    FragmentTaskView, ResourceRecommendView, ResourceFavoriteView,
    AutoTaskView, AutoTaskCancelView, TestAIGeneratePlanView,
    TaskListCreateView, TaskDetailView, TaskStartView, TaskPauseView,
    PomodoroSessionListCreateView, PomodoroSessionDetailView
)

urlpatterns = [

    # 自动执行任务路由
    path('tasks/auto_execute', AutoTaskView.as_view()),  # 设置自动执行
    path('tasks/auto_execute/<str:task_id>/cancel', AutoTaskCancelView.as_view()),  # 取消自动执行
    # 任务路由
    path('tasks', TaskListCreateView.as_view()),  # 列表和创建
    path('tasks/<str:task_id>', TaskDetailView.as_view()),  # 详情、更新和删除
    path('tasks/<str:task_id>/start', TaskStartView.as_view()),  # 启动任务
    path('tasks/<str:task_id>/pause', TaskPauseView.as_view()),  # 暂停/重启任务

    # 学习计划路由
    path('plans', PlanCreateView.as_view()),  # 创建计划
    path('plans/<str:plan_id>', PlanDetailView.as_view(), {'view_type': 'plan'}),  # 获取计划详情
    path('plans/<str:plan_id>/start', PlanStartView.as_view()),  # 启动计划
    path('plans/<str:plan_id>/pause', PlanPauseResumeView.as_view()),  # 暂停/重启计划

    # 碎片任务路由
    path('fragment_tasks', FragmentTaskView.as_view()),  # 任务碎片化

    # 学习资源路由
    path('resources/recommend', ResourceRecommendView.as_view()),  # 推荐资源
    path('resources/<str:resource_id>/favorite', ResourceFavoriteView.as_view()),  # 收藏资源

    # 情绪分析路由
    path('emotions/analysis', EmotionAnalysisView.as_view()),  # 情绪分析
    path('emotions/history', EmotionHistoryView.as_view()),  # 情绪历史

    # 语音助手路由
    path('voice/assistant', VoiceAssistantView.as_view()),  # 语音助手

    # AI计划路由
    path('ai/generate_plan', AIGeneratePlanView.as_view()),  # 生成计划
    path('ai/generate_plan/test', TestAIGeneratePlanView.as_view()),  # 测试用端点，无需认证
    path('ai/analyze_plan', AIAnalyzePlanView.as_view()),  # 分析计划
    path('ai/plans/<str:plan_id>', AIPlanDetailView.as_view()),  # 计划详情

    # 番茄钟会话路由
    path('pomodoro/sessions', PomodoroSessionListCreateView.as_view()),  # 列表和创建
    path('pomodoro/sessions/<str:session_id>', PomodoroSessionDetailView.as_view()),  # 详情和更新
]
