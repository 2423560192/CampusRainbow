from celery import shared_task
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import time
import os
import random
import hashlib
import json
import requests
from pathlib import Path

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(
    name="send_welcome_email",
    queue="users",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 5},
    retry_jitter=True
)
def send_welcome_email(user_id):
    """
    发送欢迎邮件任务
    """
    try:
        # 添加耗时的IO操作 - 读写临时文件
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_file = temp_dir / f"welcome_email_{user_id}_{int(time.time())}.json"
        
        # CPU密集型操作 - 计算大量哈希
        start_time = time.time()
        hashed_values = []
        for i in range(200000):  # 执行大量哈希计算，这会消耗CPU
            hashed_values.append(hashlib.sha256(f"{user_id}_{i}".encode()).hexdigest())
        
        # 模拟网络延迟
        time.sleep(2)
        
        # 写入大文件
        with open(temp_file, 'w') as f:
            user = User.objects.get(id=user_id)
            email_data = {
                "user_id": user_id,
                "username": user.username,
                "email": user.email,
                "send_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "template_data": {
                    "subject": "欢迎加入校园云宝！",
                    "preview_text": "感谢注册我们的服务",
                    "intro_text": f"你好 {user.username}，感谢你注册校园云宝！我们期待你的使用。",
                    "hash_sample": hashed_values[:5]  # 只保存前5个哈希值
                }
            }
            json.dump(email_data, f, indent=2)
        
        # 模拟发送邮件
        send_mail(
            subject="欢迎加入校园云宝！",
            message=f"你好 {user.username}，感谢你注册校园云宝！我们期待你的使用。",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        # 读取文件并删除
        with open(temp_file, 'r') as f:
            data = json.load(f)
        
        os.remove(temp_file)
        
        execution_time = time.time() - start_time
        logger.info(f"欢迎邮件已发送给用户 {user_id}，耗时 {execution_time:.2f} 秒")
        return {"status": "success", "execution_time": execution_time}
    except Exception as e:
        logger.error(f"发送欢迎邮件失败: {str(e)}")
        raise

@shared_task(
    name="sync_user_profile",
    queue="users",
    rate_limit="100/m"
)
def sync_user_profile(user_id, data):
    """
    同步用户配置文件到其他系统
    """
    try:
        # 模拟多个外部系统的耗时操作
        systems = ["CRM", "ERP", "Analytics", "Marketing"]
        results = {}
        
        for system in systems:
            # 模拟网络请求延迟
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
            
            # 模拟API请求
            logger.info(f"同步用户 {user_id} 到系统 {system}，延迟 {delay:.2f} 秒")
            
            # 模拟一些数据处理
            processed_data = {k: v for k, v in data.items()}  # 复制数据
            processed_data["system"] = system
            processed_data["sync_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 生成一些随机数据以增加处理量
            for i in range(100):
                processed_data[f"field_{i}"] = hashlib.md5(f"{user_id}_{system}_{i}".encode()).hexdigest()
            
            # 模拟写入本地文件
            temp_dir = Path(settings.BASE_DIR) / "temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            with open(temp_dir / f"sync_{user_id}_{system}.json", 'w') as f:
                json.dump(processed_data, f)
            
            results[system] = {
                "status": "success", 
                "sync_time": processed_data["sync_time"],
                "delay": delay
            }
        
        # 模拟一些最终处理
        time.sleep(1)
        logger.info(f"用户配置文件已同步到所有系统 {user_id}")
        return {"status": "success", "systems": results}
    except Exception as e:
        logger.error(f"同步用户配置文件失败: {str(e)}")
        raise

@shared_task(
    name="cleanup_expired_tokens",
    queue="users"
)
def cleanup_expired_tokens():
    """
    清理过期的令牌，可以作为定期任务运行
    """
    try:
        # 模拟大量数据处理
        start_time = time.time()
        
        # 模拟从数据库加载大量token数据
        token_count = 10000
        fake_tokens = []
        
        for i in range(token_count):
            token_data = {
                "id": i,
                "jti": hashlib.sha256(f"token_{i}".encode()).hexdigest(),
                "user_id": random.randint(1, 1000),
                "created_at": f"2024-{random.randint(1, 4)}-{random.randint(1, 28)}",
                "expires_at": f"2024-{random.randint(4, 12)}-{random.randint(1, 28)}",
                "is_blacklisted": random.choice([True, False])
            }
            fake_tokens.append(token_data)
        
        # 模拟数据处理，过滤过期令牌
        current_date = time.strftime("%Y-%m-%d")
        expired_tokens = [t for t in fake_tokens if t["expires_at"] < current_date and not t["is_blacklisted"]]
        
        # 模拟批量处理
        batch_size = 100
        for i in range(0, len(expired_tokens), batch_size):
            batch = expired_tokens[i:i+batch_size]
            # 模拟批量更新操作
            time.sleep(0.5)
            logger.info(f"已处理 {i+len(batch)}/{len(expired_tokens)} 个过期令牌")
        
        # 模拟写入结果到文件
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        with open(temp_dir / f"token_cleanup_{int(time.time())}.log", 'w') as f:
            f.write(f"清理开始时间: {start_time}\n")
            f.write(f"总token数: {token_count}\n")
            f.write(f"过期token数: {len(expired_tokens)}\n")
            f.write(f"清理完成时间: {time.time()}\n")
            f.write(f"总耗时: {time.time() - start_time:.2f} 秒\n")
        
        execution_time = time.time() - start_time
        logger.info(f"已清理过期令牌，共 {len(expired_tokens)} 个，耗时 {execution_time:.2f} 秒")
        return {
            "status": "success", 
            "total_tokens": token_count,
            "expired_tokens": len(expired_tokens),
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"清理过期令牌失败: {str(e)}")
        raise 