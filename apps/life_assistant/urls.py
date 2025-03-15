# 生活助手模块路由
from django.urls import path
from . import views

urlpatterns = [
    # 获取天气信息
    path('weather/', views.WeatherView.as_view(), name='weather'),
    # 跟踪校园快递
    path('express/track/', views.ExpressTrackView.as_view(), name='track_express'),
    # 宿舍待办事项管理
    path('dormitory/tasks/', views.DormitoryTasksView.as_view(), name='dormitory_tasks'),
] 