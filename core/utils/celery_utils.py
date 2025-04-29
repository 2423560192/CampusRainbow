"""
Celery 工具函数
"""
from celery.result import AsyncResult
from django.core.cache import cache
import json
from functools import wraps
import logging
import time

logger = logging.getLogger(__name__)

def get_task_result(task_id):
    """
    获取任务结果
    
    Args:
        task_id: Celery 任务 ID
        
    Returns:
        dict: 包含任务状态和结果的字典
    """
    task_result = AsyncResult(task_id)
    
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None
    }
    
    if task_result.successful():
        result["result"] = task_result.result
    elif task_result.failed():
        result["error"] = str(task_result.result)
    
    return result

def cache_task_result(task_id, result, expires=3600):
    """
    将任务结果缓存到Redis
    
    Args:
        task_id: 任务ID
        result: 任务结果
        expires: 过期时间（秒）
    """
    cache_key = f"task_result_{task_id}"
    cache.set(cache_key, json.dumps(result), expires)

def get_cached_task_result(task_id):
    """
    从缓存获取任务结果
    
    Args:
        task_id: 任务ID
        
    Returns:
        dict 或 None: 缓存的任务结果，如果没有缓存则返回None
    """
    cache_key = f"task_result_{task_id}"
    result = cache.get(cache_key)
    
    if result:
        return json.loads(result)
    
    return None

def task_with_cache(expires=3600):
    """
    将任务结果缓存的装饰器
    
    Args:
        expires: 缓存过期时间（秒）
        
    Returns:
        decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行原始任务
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 记录执行时间
            logger.info(f"Task {func.__name__} executed in {execution_time:.2f} seconds")
            
            # 如果任务有request属性和任务ID，缓存结果
            # 注意：这只在任务是通过装饰器定义的Celery任务时有效
            if hasattr(wrapper, 'request') and wrapper.request.id:
                task_id = wrapper.request.id
                cache_task_result(task_id, result, expires)
                logger.info(f"Cached result for task {task_id}")
                
            return result
        return wrapper
    return decorator

def retry_on_exception(max_retries=3, retry_delay=1, exceptions=(Exception,)):
    """
    异常重试装饰器
    
    Args:
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        exceptions: 要捕获的异常类型元组
        
    Returns:
        decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    retries += 1
                    
                    if retries <= max_retries:
                        logger.warning(f"Retry {retries}/{max_retries} for {func.__name__} due to {str(e)}")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        
            # 如果达到最大重试次数仍失败，则抛出最后一个异常
            raise last_exception
            
        return wrapper
    return decorator 