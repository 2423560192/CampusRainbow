from django.urls import path
from .views import TaskStatusView

urlpatterns = [
    path('tasks/<str:task_id>/status/', TaskStatusView.as_view(), name='task-status'),
] 