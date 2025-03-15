# 校园规划模块路由
from django.urls import path
from . import views

urlpatterns = [
    # AI 日程规划
    path('schedules/generate/', views.ScheduleGenerateView.as_view(), name='generate_schedule'),
    # 校园搭子助手匹配
    path('partners/match/', views.PartnerMatchView.as_view(), name='match_partner'),
] 