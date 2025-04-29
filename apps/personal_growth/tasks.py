from celery import shared_task
from django.utils import timezone
from .models import Plan
import time
import logging
import random

logger = logging.getLogger(__name__)

@shared_task
def complete_task_after_time(task_id):
    """
    在指定时间后完成任务
    """
    try:
        plan = Plan.objects.get(id=task_id, status='active')
        
        # 计算已完成的专注时间
        if plan.start_time:
            elapsed_time = (timezone.now() - plan.start_time).total_seconds() / 60
            plan.completed_focus_time += int(elapsed_time)
            
            # 如果设置了存钱计划，计算解锁金额
            if plan.savings_amount:
                # 按比例计算解锁金额
                completion_ratio = min(plan.completed_focus_time / plan.focus_time, 1.0)
                plan.unlocked_savings = plan.savings_amount * completion_ratio
        
        # 更新状态为已完成
        plan.status = 'completed'
        plan.save()
        
        return f"Task {task_id} completed successfully"
    except Plan.DoesNotExist:
        return f"Task {task_id} not found or not active"
    except Exception as e:
        return f"Error completing task {task_id}: {str(e)}"

@shared_task(
    name="create_task_plan",
    queue="personal_growth",
    rate_limit="100/m"
)
def create_task_plan(user_id, task_data):
    """
    异步创建任务计划
    
    Args:
        user_id: 用户ID
        task_data: 任务数据字典
    
    Returns:
        dict: 创建的任务信息
    """
    from django.contrib.auth import get_user_model
    from .serializers import TaskCreateSerializer
    
    User = get_user_model()
    
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 模拟耗时操作
        time.sleep(random.uniform(0.5, 2.0))  # 随机等待0.5-2秒，模拟繁重处理
        
        # 获取用户
        user = User.objects.get(id=user_id)
        
        # 准备序列化器上下文
        context = {'request': type('obj', (object,), {'user': user})}
        
        # 创建任务
        serializer = TaskCreateSerializer(data=task_data, context=context)
        if serializer.is_valid():
            plan = serializer.save()
            
            # 模拟一些CPU密集型操作
            for i in range(50000):
                _ = i * i
            
            # 计算执行时间
            execution_time = time.time() - start_time
            logger.info(f"任务创建成功，任务ID: {plan.id}，耗时: {execution_time:.2f}秒")
            
            # 返回任务信息
            return {
                "task_id": str(plan.id),
                "title": plan.task_name,
                "status": plan.status,
                "created_at": plan.created_at.isoformat()
            }
        else:
            logger.error(f"任务创建失败: {serializer.errors}")
            return {"error": serializer.errors}
    
    except Exception as e:
        logger.error(f"创建任务计划时出错: {str(e)}")
        return {"error": str(e)} 