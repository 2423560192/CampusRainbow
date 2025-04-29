#!/usr/bin/env python
"""
Celery异步任务测试脚本

此脚本用于测试和对比同步执行和异步执行Celery任务的性能差异
"""
import os
import sys
import time
import argparse
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoyuanyunbao.settings')
django.setup()

# 在Django设置后导入Celery任务
from apps.user.tasks import send_welcome_email, sync_user_profile, cleanup_expired_tokens
from apps.life_assistant.tasks import fetch_weather_data, track_express_package, sync_dormitory_tasks
from apps.virtual_study_room.tasks import process_join_study_room, upload_to_blockchain, ai_host_study_session

def test_sync_execution(task_name, *args, **kwargs):
    """同步测试任务执行"""
    print(f"开始同步执行任务: {task_name}")
    start_time = time.time()
    
    # 根据任务名选择要执行的任务
    if task_name == "send_welcome_email":
        result = send_welcome_email(*args, **kwargs)
    elif task_name == "sync_user_profile":
        result = sync_user_profile(*args, **kwargs)
    elif task_name == "cleanup_expired_tokens":
        result = cleanup_expired_tokens(*args, **kwargs)
    elif task_name == "fetch_weather_data":
        result = fetch_weather_data(*args, **kwargs)
    elif task_name == "track_express_package":
        result = track_express_package(*args, **kwargs)
    elif task_name == "sync_dormitory_tasks":
        result = sync_dormitory_tasks(*args, **kwargs)
    elif task_name == "process_join_study_room":
        result = process_join_study_room(*args, **kwargs)
    elif task_name == "upload_to_blockchain":
        result = upload_to_blockchain(*args, **kwargs)
    elif task_name == "ai_host_study_session":
        result = ai_host_study_session(*args, **kwargs)
    else:
        raise ValueError(f"未知任务: {task_name}")
    
    execution_time = time.time() - start_time
    print(f"任务 {task_name} 同步执行完成，耗时: {execution_time:.2f} 秒")
    return result, execution_time

def test_async_execution(task_name, *args, **kwargs):
    """异步测试任务执行"""
    print(f"开始异步执行任务: {task_name}")
    start_time = time.time()
    
    # 根据任务名选择要执行的任务
    if task_name == "send_welcome_email":
        task = send_welcome_email.delay(*args, **kwargs)
    elif task_name == "sync_user_profile":
        task = sync_user_profile.delay(*args, **kwargs)
    elif task_name == "cleanup_expired_tokens":
        task = cleanup_expired_tokens.delay(*args, **kwargs)
    elif task_name == "fetch_weather_data":
        task = fetch_weather_data.delay(*args, **kwargs)
    elif task_name == "track_express_package":
        task = track_express_package.delay(*args, **kwargs)
    elif task_name == "sync_dormitory_tasks":
        task = sync_dormitory_tasks.delay(*args, **kwargs)
    elif task_name == "process_join_study_room":
        task = process_join_study_room.delay(*args, **kwargs)
    elif task_name == "upload_to_blockchain":
        task = upload_to_blockchain.delay(*args, **kwargs)
    elif task_name == "ai_host_study_session":
        task = ai_host_study_session.delay(*args, **kwargs)
    else:
        raise ValueError(f"未知任务: {task_name}")
    
    # 非阻塞的异步任务执行，这里只记录排队时间
    enqueue_time = time.time() - start_time
    print(f"任务 {task_name} 已加入队列，耗时: {enqueue_time:.2f} 秒")
    print(f"任务ID: {task.id}")
    
    # 如果要等待结果完成可以取消下面的注释
    # print("等待任务完成...")
    # result = task.get()
    # execution_time = time.time() - start_time
    # print(f"任务 {task_name} 异步执行完成，总耗时: {execution_time:.2f} 秒")
    # return result, execution_time
    
    return task.id, enqueue_time

def check_task_status(task_id):
    """检查任务状态"""
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    print(f"任务 {task_id} 状态: {result.status}")
    
    if result.ready():
        if result.successful():
            print("任务成功完成!")
            print(f"结果: {result.result}")
        else:
            print("任务失败!")
            print(f"错误: {result.result}")
    else:
        print("任务仍在执行中...")
    
    return result.status, result.result if result.ready() else None

def run_demo():
    """运行演示测试"""
    print("\n===== 校园云宝Celery异步任务测试 =====\n")
    
    # 测试天气数据获取
    print("\n1. 测试天气数据获取")
    print("同步执行...")
    _, sync_time = test_sync_execution("fetch_weather_data", "北京")
    
    print("\n异步执行...")
    task_id, async_time = test_async_execution("fetch_weather_data", "上海")
    
    print(f"\n性能对比: 同步耗时 {sync_time:.2f} 秒 vs 异步入队耗时 {async_time:.2f} 秒")
    print(f"响应速度提升: {(sync_time - async_time) / sync_time * 100:.2f}%")
    
    # 检查任务状态(可选)
    answer = input("\n是否等待任务完成并查看结果? (y/n): ")
    if answer.lower() == 'y':
        while True:
            status, result = check_task_status(task_id)
            if status in ['SUCCESS', 'FAILURE']:
                break
            print("等待5秒后重新检查...")
            time.sleep(5)
    
    # 测试区块链上传
    print("\n2. 测试区块链上传")
    record = {
        "study_time": 3600,  # 1小时
        "focus_score": 0.85,
        "completed_tasks": 3
    }
    
    print("同步执行...")
    _, sync_time = test_sync_execution("upload_to_blockchain", "test_user_1", record)
    
    print("\n异步执行...")
    task_id, async_time = test_async_execution("upload_to_blockchain", "test_user_2", record)
    
    print(f"\n性能对比: 同步耗时 {sync_time:.2f} 秒 vs 异步入队耗时 {async_time:.2f} 秒")
    print(f"响应速度提升: {(sync_time - async_time) / sync_time * 100:.2f}%")
    
    # 测试AI会话
    print("\n3. 测试AI自习室会话")
    print("同步执行...")
    _, sync_time = test_sync_execution("ai_host_study_session", "test_room_1")
    
    print("\n异步执行...")
    task_id, async_time = test_async_execution("ai_host_study_session", "test_room_2")
    
    print(f"\n性能对比: 同步耗时 {sync_time:.2f} 秒 vs 异步入队耗时 {async_time:.2f} 秒")
    print(f"响应速度提升: {(sync_time - async_time) / sync_time * 100:.2f}%")
    
    print("\n===== 测试完成 =====")
    print("异步任务将在后台继续执行，可以使用以下命令查看Worker日志:")
    print("python start_celery.py --loglevel=INFO")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试Celery异步任务")
    parser.add_argument("--task", type=str, help="要测试的任务名称")
    parser.add_argument("--mode", type=str, choices=["sync", "async"], default="async", help="执行模式")
    parser.add_argument("--check", type=str, help="检查指定ID的任务状态")
    parser.add_argument("--demo", action="store_true", help="运行演示测试")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
    elif args.check:
        check_task_status(args.check)
    elif args.task:
        if args.mode == "sync":
            test_sync_execution(args.task)
        else:
            test_async_execution(args.task)
    else:
        parser.print_help() 