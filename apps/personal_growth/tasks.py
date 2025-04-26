from celery import shared_task
from django.utils import timezone
from .models import Plan

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