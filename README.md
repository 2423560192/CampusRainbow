# CampusRainbow
"校园云宝"小程序旨在为校园群体提供一个基于AI驱动的个人助手，集成学业效率管理、生活便捷支持和社交激励功能，特别优化碎片化时间使用，帮助学生高效利用零散时间完成学习和生活任务，通过虚拟自习室和区块链技术提升专注度、数据可信度和用户参与度。

## 功能模块

### 1. 个人提升模块

个人提升模块提供以下功能：

- **学习计划管理**：创建、查看、更新和暂停/重启学习计划
- **AI 生成学习计划**：根据长期目标自动生成详细学习计划
- **碎片化任务拆解**：将大任务拆解为5-15分钟的微任务
- **学习资源推荐**：根据当前任务推荐适合的学习资源
- **情绪分析与调节**：分析学习情绪并提供调节建议
- **语音助手控制**：通过语音指令控制任务执行
- **自动任务执行**：设置自动执行的任务

### 2. 校园规划模块

### 3. 虚拟自习室模块

### 4. 生活助手模块

## 技术架构

- 后端：Django 4.2 + Django REST Framework
- 数据库：MySQL
- 认证：JWT (JSON Web Token)
- API文档：OpenAPI 3.0
- 异步任务处理：Celery + Redis（高并发支持）
- 消息队列：Redis
- 缓存：Redis

## 高并发设计

系统使用Celery和Redis实现高并发任务处理，主要包括：

1. **多队列设计**：根据不同应用模块设置独立的任务队列
   - users：用户相关操作（注册、资料更新）
   - life_assistant：生活助手任务（天气查询、快递跟踪）
   - study_room：虚拟自习室任务（区块链记录、AI主持）
   - personal_growth：个人提升相关任务
   - campus_planning：校园规划相关任务

2. **任务分发**：使用Redis作为消息代理，实现任务的高效分发和处理

3. **异步处理**：将耗时操作（如邮件发送、第三方API调用）异步处理，避免阻塞主进程

4. **结果缓存**：使用Redis缓存任务结果，提高重复查询性能

5. **错误处理**：实现了自动重试、退避策略等容错机制

## 安装与设置

1. 克隆代码库并安装依赖：
```bash
git clone [仓库链接]
cd CampusRainbow
pip install -r requirements.txt
```

2. 配置Redis：
```bash
# Windows下使用Docker安装Redis
docker run --name yunbao-redis -p 6379:6379 -d redis

# 或在Linux下安装
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

3. 设置环境变量（创建.env文件）：
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=yunbao
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 运行项目

1. 启动Django服务器：
```bash
python manage.py migrate
python manage.py runserver
```

2. 启动Celery Worker（各种启动方式）：

```bash
# 启动所有队列的worker
python start_celery.py

# 启动特定队列的worker
python start_celery.py --queue=users,default

# 启动高并发worker
python start_celery.py --concurrency=4

# 启动定时任务调度器
python start_celery.py --beat

# 启动Flower监控界面
python start_celery.py --flower
```

## API文档

API文档可以通过访问项目根路径下的'校园云宝.openapi.json'文件获取。
