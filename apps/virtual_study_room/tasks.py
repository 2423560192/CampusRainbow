from celery import shared_task
import logging
import time
import json
from django.conf import settings
import os
import random
import hashlib
import numpy as np
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont
import csv
import matplotlib.pyplot as plt
import io
import base64

logger = logging.getLogger(__name__)

@shared_task(
    name="process_join_study_room",
    queue="study_room",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3}
)
def process_join_study_room(user_id, room_id):
    """
    处理加入自习室请求
    """
    try:
        start_time = time.time()
        logger.info(f"处理用户 {user_id} 加入自习室 {room_id} 的请求")
        
        # 模拟数据库查询延迟
        time.sleep(random.uniform(0.5, 1.0))
        
        # 模拟一系列验证操作
        # 1. 检查用户权限
        time.sleep(0.3)
        user_permissions = ["join_room", "chat", "view_statistics"]
        
        # 2. 检查房间状态和容量
        time.sleep(0.5)
        room_capacity = random.randint(10, 50)
        current_members = random.randint(0, room_capacity - 1)  # 确保有空位
        room_status = "active" if random.random() < 0.9 else "maintenance"
        
        # 模拟一些CPU密集计算 - 生成房间的统计数据
        member_data = []
        for i in range(current_members):
            member_data.append({
                "user_id": f"user_{random.randint(1000, 9999)}",
                "join_time": time.time() - random.uniform(0, 3600),
                "focus_score": random.uniform(0.3, 1.0),
                "total_study_time": random.randint(300, 7200)  # 5分钟到2小时
            })
        
        # 计算一些统计数据
        if member_data:
            focus_scores = [m["focus_score"] for m in member_data]
            avg_focus = sum(focus_scores) / len(focus_scores)
            study_times = [m["total_study_time"] for m in member_data]
            avg_study_time = sum(study_times) / len(study_times)
        else:
            avg_focus = 0
            avg_study_time = 0
            
        # 模拟生成图表
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 使用matplotlib生成一个图表
        plt.figure(figsize=(10, 6))
        
        # 创建一个随机数据的图表
        x = np.arange(24)  # 24小时
        y = np.random.randint(0, current_members + 5, size=24)  # 每小时的成员数
        
        plt.bar(x, y, color='skyblue')
        plt.xlabel('小时')
        plt.ylabel('自习室成员数')
        plt.title(f'自习室 {room_id} 每小时成员分布')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 保存图表
        chart_file = temp_dir / f"study_room_{room_id}_stats_{int(time.time())}.png"
        plt.savefig(chart_file)
        plt.close()
        
        # 将新成员添加到房间 - 模拟数据库操作
        time.sleep(0.8)
        
        # 模拟创建用户与房间的关联记录
        join_record = {
            "user_id": user_id,
            "room_id": room_id,
            "join_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": f"session_{hashlib.md5(f'{user_id}_{room_id}_{time.time()}'.encode()).hexdigest()[:10]}",
            "device_info": {
                "type": random.choice(["PC", "Mobile", "Tablet"]),
                "os": random.choice(["Windows", "MacOS", "iOS", "Android"]),
                "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"])
            }
        }
        
        # 写入加入记录
        record_file = temp_dir / f"join_record_{user_id}_{room_id}_{int(time.time())}.json"
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(join_record, f, ensure_ascii=False, indent=2)
        
        # 模拟通知其他成员
        for member in member_data:
            # 模拟每个通知需要的时间
            time.sleep(0.05)
        
        # 模拟初始化用户会话资源
        time.sleep(1.2)
        
        # 计算处理总时间
        execution_time = time.time() - start_time
        logger.info(f"用户 {user_id} 已加入自习室 {room_id}，耗时 {execution_time:.2f} 秒")
        
        # 返回结果
        return {
            "user_id": user_id,
            "room_id": room_id,
            "status": "joined" if room_status == "active" else "failed",
            "joined_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "room_stats": {
                "capacity": room_capacity,
                "current_members": current_members + 1,  # 包括新加入的成员
                "avg_focus_score": avg_focus,
                "avg_study_time": avg_study_time,
                "chart_file": str(chart_file)
            },
            "session_id": join_record["session_id"],
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"加入自习室失败: {str(e)}")
        raise

@shared_task(
    name="upload_to_blockchain",
    queue="study_room",
    rate_limit="5/m",
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={'max_retries': 5},
    retry_jitter=True
)
def upload_to_blockchain(user_id, study_record):
    """
    将学习记录上传到区块链
    """
    try:
        start_time = time.time()
        logger.info(f"开始处理用户 {user_id} 的学习记录上传到区块链")
        
        # 模拟预处理数据
        time.sleep(random.uniform(0.5, 1.0))
        
        # 生成完整的记录数据(如果传入的不完整)
        if isinstance(study_record, dict):
            complete_record = study_record.copy()
        else:
            # 如果只传入基本信息，创建完整记录
            complete_record = {
                "user_id": user_id,
                "study_time": random.randint(1800, 14400),  # 30分钟到4小时
                "focus_score": random.uniform(0.6, 1.0),
                "completed_tasks": random.randint(1, 10),
                "timestamp": int(time.time())
            }
        
        # 确保记录有必要的字段
        if "timestamp" not in complete_record:
            complete_record["timestamp"] = int(time.time())
        if "study_time" not in complete_record:
            complete_record["study_time"] = random.randint(1800, 14400)
        
        # 添加一些额外的元数据
        complete_record["upload_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        complete_record["client_ip"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        # 模拟数据整理和验证
        time.sleep(0.8)
        
        # 模拟区块链数据准备 - 这是个CPU密集型操作
        # 1. 生成数据哈希
        data_str = json.dumps(complete_record, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # 2. 模拟工作量证明计算(CPU密集)
        nonce = 0
        target_prefix = "0" * 4  # 要求前面有4个0
        proof_hash = ""
        
        proof_start = time.time()
        while True:
            test_str = f"{data_hash}:{nonce}"
            proof_hash = hashlib.sha256(test_str.encode()).hexdigest()
            if proof_hash.startswith(target_prefix):
                break
            nonce += 1
            # 为了不让这个循环真的耗费太多时间，设置一个限制
            if nonce > 10000 or time.time() - proof_start > 3:
                break
        
        logger.info(f"完成工作量证明，尝试了 {nonce} 次，耗时 {time.time() - proof_start:.2f} 秒")
        
        # 模拟区块链交易准备
        blockchain_data = {
            "data": complete_record,
            "hash": data_hash,
            "proof": {
                "nonce": nonce,
                "hash": proof_hash
            },
            "meta": {
                "timestamp": int(time.time()),
                "user_agent": "CampusRainbow Blockchain Client v1.0",
                "network": "TestNet"
            }
        }
        
        # 模拟区块链网络延迟和验证
        time.sleep(random.uniform(2.0, 5.0))
        
        # 创建一些可视化数据
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存区块链数据
        blockchain_file = temp_dir / f"blockchain_tx_{user_id}_{int(time.time())}.json"
        with open(blockchain_file, 'w', encoding='utf-8') as f:
            json.dump(blockchain_data, f, ensure_ascii=False, indent=2)
        
        # 创建学习统计图表
        plt.figure(figsize=(12, 8))
        
        # 左侧图表 - 专注度统计
        plt.subplot(2, 2, 1)
        focus_data = [random.uniform(0.3, 1.0) for _ in range(12)]
        focus_data.append(complete_record["focus_score"] if "focus_score" in complete_record else random.uniform(0.7, 1.0))
        plt.plot(range(len(focus_data)), focus_data, marker='o', linestyle='-', color='blue')
        plt.axhline(y=sum(focus_data)/len(focus_data), color='r', linestyle='--', alpha=0.7)
        plt.title('专注度趋势')
        plt.xlabel('学习会话')
        plt.ylabel('专注度分数')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 右侧图表 - 学习时长
        plt.subplot(2, 2, 2)
        time_data = [random.randint(1200, 10800) for _ in range(7)]  # 过去7天的学习时间
        time_data.append(complete_record["study_time"] if "study_time" in complete_record else random.randint(1800, 7200))
        days = ["一", "二", "三", "四", "五", "六", "日", "今天"]
        plt.bar(days, [t/3600 for t in time_data], color='green')  # 转换为小时
        plt.title('每日学习时长')
        plt.xlabel('星期')
        plt.ylabel('小时')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 底部图表 - 区块链交易历史
        plt.subplot(2, 1, 2)
        tx_history = [random.randint(1, 5) for _ in range(30)]  # 每天的交易数
        plt.plot(range(len(tx_history)), tx_history, marker='', linestyle='-', color='purple')
        plt.fill_between(range(len(tx_history)), tx_history, alpha=0.2, color='purple')
        plt.title('区块链交易历史')
        plt.xlabel('天数')
        plt.ylabel('交易数量')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # 保存图表
        chart_file = temp_dir / f"blockchain_stats_{user_id}_{int(time.time())}.png"
        plt.savefig(chart_file)
        plt.close()
        
        # 生成模拟交易ID
        transaction_id = f"tx_{hashlib.sha256(f'{user_id}_{time.time()}'.encode()).hexdigest()[:16]}"
        
        # 写入CSV格式的交易日志
        csv_file = temp_dir / f"blockchain_tx_log_{user_id}.csv"
        csv_exists = os.path.exists(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not csv_exists:
                writer.writerow(["交易ID", "用户ID", "时间戳", "学习时长(秒)", "专注度", "完成任务数", "上传时间"])
            
            writer.writerow([
                transaction_id,
                user_id,
                complete_record["timestamp"],
                complete_record.get("study_time", "N/A"),
                complete_record.get("focus_score", "N/A"),
                complete_record.get("completed_tasks", "N/A"),
                complete_record["upload_time"]
            ])
        
        execution_time = time.time() - start_time
        logger.info(f"用户 {user_id} 的学习记录已上传到区块链，交易ID: {transaction_id}，耗时 {execution_time:.2f} 秒")
        
        return {
            "user_id": user_id,
            "transaction_id": transaction_id,
            "status": "confirmed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time": execution_time,
            "blockchain_file": str(blockchain_file),
            "chart_file": str(chart_file),
            "record_summary": {
                "study_time": complete_record.get("study_time", 0) / 60,  # 转换为分钟
                "focus_score": complete_record.get("focus_score", 0),
                "completed_tasks": complete_record.get("completed_tasks", 0)
            }
        }
    except Exception as e:
        logger.error(f"上传到区块链失败: {str(e)}")
        raise

@shared_task(
    name="ai_host_study_session",
    queue="study_room",
    time_limit=300,  # 5分钟时间限制
    soft_time_limit=240  # 4分钟软时间限制
)
def ai_host_study_session(room_id, session_config=None):
    """
    AI主持自习室会话
    """
    try:
        start_time = time.time()
        logger.info(f"开始AI主持自习室 {room_id} 会话")
        
        # 如果没有提供配置，使用默认配置
        if not session_config:
            session_config = {
                "duration_minutes": random.randint(25, 120),
                "break_interval": random.randint(25, 50),
                "break_duration": random.randint(5, 15),
                "topic": random.choice(["数学", "英语", "物理", "化学", "生物", "历史", "地理", "编程"]),
                "difficulty": random.choice(["初级", "中级", "高级"]),
                "mode": random.choice(["自由模式", "专注模式", "竞赛模式"])
            }
        
        # 模拟AI模型加载 - 这是个CPU密集型操作
        time.sleep(random.uniform(1.5, 3.0))
        
        # 模拟生成AI提示和引导内容
        prompts = [
            f"欢迎来到{session_config.get('topic', '学习')}自习室，本次学习时长为{session_config.get('duration_minutes', 60)}分钟",
            f"每{session_config.get('break_interval', 30)}分钟会有一个{session_config.get('break_duration', 5)}分钟的休息时间",
            "请保持专注，减少环境干扰",
            "建议关闭手机通知，并准备好学习所需材料",
            "学习期间可以适当补充水分，保持大脑活力",
            "有任何问题可以随时在聊天区提问"
        ]
        
        # 模拟会话初始化 - 生成随机参与者
        participant_count = random.randint(5, 20)
        participants = []
        
        for i in range(participant_count):
            participant = {
                "user_id": f"user_{random.randint(1000, 9999)}",
                "name": f"学员{i+1}",
                "join_time": time.time() - random.uniform(0, 600),  # 0-10分钟前加入
                "avatar": f"avatar_{random.randint(1, 20)}.png"
            }
            participants.append(participant)
        
        # 模拟AI生成的学习材料
        study_materials = []
        for i in range(random.randint(3, 8)):
            material = {
                "title": f"{session_config.get('topic', '学习')}资料 {i+1}",
                "type": random.choice(["文档", "视频", "练习题", "图表"]),
                "difficulty": random.choice(["初级", "中级", "高级"]),
                "url": f"https://example.com/materials/{session_config.get('topic', 'study')}/{random.randint(1000, 9999)}"
            }
            study_materials.append(material)
            
        # 模拟AI分析学习风格和生成个性化建议
        time.sleep(1.5)
        
        # 模拟创建自习室环境 - 生成背景音乐和环境声音
        ambient_sounds = [
            {"name": "轻松钢琴曲", "duration": "30:00", "volume": 0.4},
            {"name": "自然雨声", "duration": "60:00", "volume": 0.3},
            {"name": "咖啡厅环境", "duration": "45:00", "volume": 0.2},
            {"name": "白噪音", "duration": "120:00", "volume": 0.25}
        ]
        
        # 模拟CPU密集型的运算 - 生成大量随机数据并分析
        matrix_size = 800
        matrix_a = np.random.rand(matrix_size, matrix_size)
        matrix_b = np.random.rand(matrix_size, matrix_size)
        result = np.dot(matrix_a, matrix_b)  # 矩阵乘法是CPU密集型的
        
        # 使用计算结果做一些简单的分析
        mean_val = np.mean(result)
        std_val = np.std(result)
        
        # 模拟生成会话报告和可视化
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 准备会话数据
        session_id = f"session_{int(time.time())}_{room_id}"
        session_data = {
            "room_id": room_id,
            "session_id": session_id,
            "config": session_config,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "expected_end_time": time.strftime(
                "%Y-%m-%d %H:%M:%S", 
                time.localtime(time.time() + session_config.get("duration_minutes", 60) * 60)
            ),
            "participants": participants,
            "prompts": prompts,
            "study_materials": study_materials,
            "ambient_sounds": ambient_sounds,
            "ai_analysis": {
                "mean_value": float(mean_val),
                "std_value": float(std_val),
                "recommended_focus_techniques": [
                    "番茄工作法",
                    "5-25-5工作法",
                    "单任务专注"
                ],
                "personalized_advice": "建议适当调整学习环境，保持坐姿正确，每25分钟后活动一下身体"
            }
        }
        
        # 保存会话数据
        session_file = temp_dir / f"ai_session_{room_id}_{int(time.time())}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        # 生成会话统计图表
        plt.figure(figsize=(12, 8))
        
        # 参与者活跃度图表
        plt.subplot(2, 2, 1)
        activity_data = [random.uniform(0.3, 1.0) for _ in range(participant_count)]
        plt.bar(range(participant_count), activity_data, color='blue')
        plt.title('参与者活跃度')
        plt.xlabel('参与者')
        plt.ylabel('活跃度分数')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 专注度随时间变化
        plt.subplot(2, 2, 2)
        times = list(range(12))  # 12个时间点
        focus_scores = [random.uniform(0.6, 1.0) for _ in range(12)]
        plt.plot(times, focus_scores, marker='o', linestyle='-', color='green')
        plt.title('专注度随时间变化')
        plt.xlabel('时间(5分钟)')
        plt.ylabel('平均专注度')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 参与者类型分布
        plt.subplot(2, 2, 3)
        types = ['视觉型', '听觉型', '动觉型', '读写型']
        type_counts = [random.randint(1, participant_count) for _ in range(4)]
        plt.pie(type_counts, labels=types, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
        plt.title('学习风格分布')
        
        # 每小时学习效率
        plt.subplot(2, 2, 4)
        hours = list(range(1, 9))  # 8小时
        efficiency = [random.uniform(0.5, 1.0) for _ in range(8)]
        plt.plot(hours, efficiency, marker='s', linestyle='-', color='purple')
        plt.title('学习效率曲线')
        plt.xlabel('小时')
        plt.ylabel('效率')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # 保存图表
        chart_file = temp_dir / f"ai_session_stats_{room_id}_{int(time.time())}.png"
        plt.savefig(chart_file)
        plt.close()
        
        execution_time = time.time() - start_time
        logger.info(f"AI已开始主持自习室 {room_id}，会话ID: {session_id}，耗时 {execution_time:.2f} 秒")
        
        # 返回会话信息
        return {
            "room_id": room_id,
            "session_id": session_id,
            "status": "active",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": session_config,
            "participant_count": participant_count,
            "execution_time": execution_time,
            "session_file": str(session_file),
            "chart_file": str(chart_file)
        }
    except Exception as e:
        logger.error(f"AI主持自习室失败: {str(e)}")
        raise 