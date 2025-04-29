from celery import shared_task
import logging
import time
import requests
from django.conf import settings
import os
import json
import random
import hashlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import csv

logger = logging.getLogger(__name__)

@shared_task(
    name="fetch_weather_data",
    queue="life_assistant",
    rate_limit="2/m",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3},
    retry_jitter=True
)
def fetch_weather_data(location):
    """
    从第三方API获取天气数据
    """
    try:
        start_time = time.time()
        logger.info(f"开始获取 {location} 的天气数据")
        
        # 模拟API请求延迟和网络不稳定
        time.sleep(random.uniform(1.5, 3.0))
        
        # 模拟多次请求重试
        for attempt in range(3):
            # 模拟网络不稳定的情况
            if random.random() < 0.3 and attempt < 2:  # 30%的概率失败，但不是最后一次尝试
                logger.warning(f"天气API请求失败，正在重试 ({attempt+1}/3)")
                time.sleep(1)
                continue
                
            # 模拟处理复杂的天气数据
            weather_data = {
                "location": location,
                "coordinates": {
                    "lat": random.uniform(18, 40),
                    "lon": random.uniform(73, 135),
                },
                "current": {
                    "temperature": f"{random.randint(15, 35)}°C",
                    "weather": random.choice(["晴", "多云", "阴", "小雨", "中雨", "大雨"]),
                    "humidity": f"{random.randint(30, 90)}%",
                    "wind_speed": f"{random.randint(0, 30)} km/h",
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "forecast": []
            }
            
            # 生成未来5天的天气预报
            for day in range(1, 6):
                forecast_date = time.localtime(time.time() + 86400 * day)
                forecast_day = {
                    "date": time.strftime("%Y-%m-%d", forecast_date),
                    "max_temp": f"{random.randint(20, 38)}°C",
                    "min_temp": f"{random.randint(15, 25)}°C",
                    "weather": random.choice(["晴", "多云", "阴", "小雨", "中雨"]),
                    "humidity": f"{random.randint(30, 90)}%",
                    "wind_speed": f"{random.randint(0, 30)} km/h",
                }
                weather_data["forecast"].append(forecast_day)
            
            # 模拟生成天气图表
            temp_dir = Path(settings.BASE_DIR) / "temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # 创建一个图表图像
            img_width, img_height = 500, 300
            image = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # 画一些模拟数据
            temps = [random.randint(15, 35) for _ in range(7)]
            max_temp = max(temps)
            min_temp = min(temps)
            
            # 绘制线条
            for i in range(len(temps) - 1):
                x1 = i * (img_width // 6) + 50
                y1 = img_height - 50 - ((temps[i] - min_temp) / (max_temp - min_temp) * 200)
                x2 = (i + 1) * (img_width // 6) + 50
                y2 = img_height - 50 - ((temps[i + 1] - min_temp) / (max_temp - min_temp) * 200)
                draw.line((x1, y1, x2, y2), fill=(0, 0, 255), width=3)
                draw.ellipse((x1 - 5, y1 - 5, x1 + 5, y1 + 5), fill=(255, 0, 0))
            
            draw.ellipse((x2 - 5, y2 - 5, x2 + 5, y2 + 5), fill=(255, 0, 0))
            
            # 保存图片
            chart_file = temp_dir / f"weather_chart_{location}_{int(time.time())}.png"
            image.save(chart_file)
            
            # 将天气数据写入CSV
            csv_file = temp_dir / f"weather_data_{location}_{int(time.time())}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "最高温度", "最低温度", "天气状况", "湿度", "风速"])
                writer.writerow(["今天", weather_data["current"]["temperature"], "-", 
                                weather_data["current"]["weather"], 
                                weather_data["current"]["humidity"], 
                                weather_data["current"]["wind_speed"]])
                
                for day in weather_data["forecast"]:
                    writer.writerow([day["date"], day["max_temp"], day["min_temp"], 
                                   day["weather"], day["humidity"], day["wind_speed"]])
            
            # 处理数据统计
            json_file = temp_dir / f"weather_{location}_{int(time.time())}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(weather_data, f, ensure_ascii=False, indent=2)
            
            # 执行一些CPU密集型的矩阵运算，模拟天气预测算法
            matrix_size = 500
            matrix_a = np.random.rand(matrix_size, matrix_size)
            matrix_b = np.random.rand(matrix_size, matrix_size)
            result = np.dot(matrix_a, matrix_b)  # 矩阵乘法是CPU密集型的
            
            # 模拟数据分析
            mean_temp = np.mean(result)
            
            execution_time = time.time() - start_time
            logger.info(f"已获取并处理{location}的天气数据，耗时 {execution_time:.2f} 秒")
            
            weather_data["execution_time"] = execution_time
            weather_data["chart_file"] = str(chart_file)
            weather_data["data_file"] = str(json_file)
            weather_data["matrix_analysis"] = {"mean": float(mean_temp)}
            
            return weather_data
            
        # 如果重试后仍然失败
        raise Exception("无法获取天气数据，多次重试后失败")
    except Exception as e:
        logger.error(f"获取天气数据失败: {str(e)}")
        raise

@shared_task(
    name="track_express_package",
    queue="life_assistant",
    rate_limit="10/m",
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={'max_retries': 3}
)
def track_express_package(tracking_number, express_company=None):
    """
    跟踪快递包裹
    """
    try:
        start_time = time.time()
        logger.info(f"开始跟踪快递: {tracking_number}, 快递公司: {express_company or '未知'}")
        
        # 模拟请求延迟
        time.sleep(random.uniform(2.0, 4.0))
        
        # 模拟爬取多个来源的快递信息
        sources = ["官方API", "第三方1", "第三方2"]
        
        tracking_results = {}
        for source in sources:
            # 模拟每个源的请求延迟
            time.sleep(random.uniform(0.8, 1.5))
            
            # 随机生成物流节点数量
            node_count = random.randint(3, 10)
            tracking_nodes = []
            
            # 生成模拟的物流节点
            current_time = time.time()
            for i in range(node_count):
                node_time = current_time - (node_count - i) * random.randint(3600, 86400)  # 每个节点间隔1-24小时
                node = {
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(node_time)),
                    "location": random.choice(["上海集散中心", "北京转运中心", "广州分拣中心", "深圳物流点", "成都站点", "重庆配送点"]),
                    "status": random.choice(["已收件", "运输中", "已到达", "派送中", "已签收"]),
                    "operator": f"操作员{random.randint(1000, 9999)}"
                }
                tracking_nodes.append(node)
            
            # 将最新状态设为当前状态
            current_status = tracking_nodes[-1]["status"] if tracking_nodes else "未查询到物流信息"
            
            tracking_results[source] = {
                "nodes": tracking_nodes,
                "current_status": current_status,
                "reliability": random.uniform(0.7, 1.0)
            }
        
        # 模拟数据汇总和分析
        combined_nodes = []
        for source, result in tracking_results.items():
            for node in result["nodes"]:
                node["source"] = source
                combined_nodes.append(node)
        
        # 按时间排序
        combined_nodes.sort(key=lambda x: x["time"])
        
        # 写入文件
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 写入JSON格式
        json_file = temp_dir / f"express_{tracking_number}_{int(time.time())}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "tracking_number": tracking_number,
                "express_company": express_company or "未知",
                "sources": tracking_results,
                "combined_nodes": combined_nodes,
                "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, ensure_ascii=False, indent=2)
        
        # 写入CSV格式
        csv_file = temp_dir / f"express_{tracking_number}_{int(time.time())}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["时间", "地点", "状态", "操作员", "数据源"])
            for node in combined_nodes:
                writer.writerow([
                    node["time"], 
                    node["location"], 
                    node["status"],
                    node["operator"],
                    node["source"]
                ])
        
        # 模拟一些复杂计算
        for _ in range(5):
            hash_value = hashlib.sha256(f"{tracking_number}_{random.random()}".encode()).hexdigest()
            time.sleep(0.2)
        
        execution_time = time.time() - start_time
        logger.info(f"已完成快递跟踪: {tracking_number}，耗时 {execution_time:.2f} 秒")
        
        # 返回结果
        return {
            "tracking_number": tracking_number,
            "express_company": express_company or "未知",
            "current_status": combined_nodes[-1]["status"] if combined_nodes else "未查询到物流信息",
            "execution_time": execution_time,
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data_files": {
                "json": str(json_file),
                "csv": str(csv_file)
            }
        }
    except Exception as e:
        logger.error(f"跟踪快递失败: {str(e)}")
        raise

@shared_task(
    name="sync_dormitory_tasks",
    queue="life_assistant"
)
def sync_dormitory_tasks(user_id, task_data=None):
    """
    同步宿舍待办事项到其他平台
    """
    try:
        start_time = time.time()
        logger.info(f"开始同步用户 {user_id} 的宿舍待办事项")
        
        # 生成随机任务数据(如果没有提供)
        if not task_data:
            task_count = random.randint(5, 20)
            task_data = []
            for i in range(task_count):
                task = {
                    "id": f"task_{int(time.time())}_{i}",
                    "title": f"宿舍任务 {i+1}",
                    "description": f"这是宿舍任务 {i+1} 的详细描述",
                    "priority": random.choice(["高", "中", "低"]),
                    "due_date": f"2024-{random.randint(1, 12)}-{random.randint(1, 28)}",
                    "status": random.choice(["待完成", "进行中", "已完成", "已过期"])
                }
                task_data.append(task)
        
        # 模拟与多个外部系统同步
        platforms = ["宿舍管理系统", "个人日历", "团队协作平台", "微信小程序"]
        sync_results = {}
        
        for platform in platforms:
            # 模拟网络请求延迟
            time.sleep(random.uniform(0.5, 1.5))
            
            # 模拟同步逻辑
            success_rate = random.uniform(0.8, 1.0)
            succeeded_tasks = []
            failed_tasks = []
            
            for task in task_data:
                if random.random() < success_rate:
                    succeeded_tasks.append(task["id"])
                else:
                    failed_tasks.append(task["id"])
            
            # 模拟一些数据处理
            time.sleep(random.uniform(0.2, 0.8))
            
            sync_results[platform] = {
                "total_tasks": len(task_data),
                "succeeded": len(succeeded_tasks),
                "failed": len(failed_tasks),
                "success_rate": len(succeeded_tasks) / len(task_data) if task_data else 0,
                "sync_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "platform_id": hashlib.md5(f"{platform}_{user_id}".encode()).hexdigest()
            }
        
        # 模拟生成报告
        temp_dir = Path(settings.BASE_DIR) / "temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        report_file = temp_dir / f"dormitory_sync_{user_id}_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "user_id": user_id,
                "task_count": len(task_data),
                "platforms": sync_results,
                "sync_date": time.strftime("%Y-%m-%d"),
                "sync_time": time.strftime("%H:%M:%S"),
                "report_id": hashlib.sha256(f"report_{user_id}_{time.time()}".encode()).hexdigest()
            }, f, ensure_ascii=False, indent=2)
        
        # 模拟数据库读写操作
        time.sleep(0.5)
        
        execution_time = time.time() - start_time
        logger.info(f"已同步用户 {user_id} 的宿舍待办事项，耗时 {execution_time:.2f} 秒")
        
        # 返回结果
        return {
            "user_id": user_id,
            "task_count": len(task_data),
            "platforms": sync_results,
            "execution_time": execution_time,
            "report_file": str(report_file)
        }
    except Exception as e:
        logger.error(f"同步宿舍待办事项失败: {str(e)}")
        raise 