#!/usr/bin/env python
"""
启动Celery Worker的帮助脚本
"""
import os
import sys
import subprocess
import argparse

def start_celery_worker(queue=None, concurrency=None, loglevel="INFO"):
    """
    启动Celery worker
    
    Args:
        queue: 队列名称，不提供则处理所有队列
        concurrency: 并发worker数量
        loglevel: 日志级别
    """
    cmd = ["celery", "-A", "xiaoyuanyunbao", "worker"]
    
    if queue:
        cmd.extend(["-Q", queue])
    
    if concurrency:
        cmd.extend(["--concurrency", str(concurrency)])
    
    cmd.extend(["--loglevel", loglevel])
    
    # 在Windows上需要添加pool参数
    if os.name == 'nt':
        cmd.extend(["--pool=solo"])
    
    print(f"启动Celery worker，命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def start_celery_beat():
    """启动Celery beat 调度器"""
    cmd = ["celery", "-A", "xiaoyuanyunbao", "beat", "--loglevel", "INFO"]
    
    print(f"启动Celery beat 调度器，命令: {' '.join(cmd)}")
    subprocess.run(cmd)

def start_flower():
    """启动Flower监控界面"""
    cmd = ["celery", "-A", "xiaoyuanyunbao", "flower"]
    
    print(f"启动Flower监控界面，命令: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="启动Celery worker或beat调度器")
    
    parser.add_argument("--queue", type=str, help="指定要处理的队列，例如: users,default")
    parser.add_argument("--concurrency", type=int, help="worker并发数")
    parser.add_argument("--loglevel", type=str, default="INFO", help="日志级别")
    parser.add_argument("--beat", action="store_true", help="启动beat调度器")
    parser.add_argument("--flower", action="store_true", help="启动flower监控")
    
    args = parser.parse_args()
    
    if args.beat:
        start_celery_beat()
    elif args.flower:
        start_flower()
    else:
        start_celery_worker(args.queue, args.concurrency, args.loglevel) 