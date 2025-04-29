# 第五章 安装及使用

## 5.1 安装环境

### 系统要求
- 操作系统：Windows 10/11、macOS 或 Linux
- Python 3.8 或更高版本
- MySQL 5.7 或更高版本
- Redis 6.0 或更高版本

### 软件依赖
- Django 4.2
- Django REST Framework 3.14
- Simple JWT
- Celery 5.2
- 其他依赖详见 requirements.txt

## 5.2 安装流程

### 步骤1：获取源代码
```
git clone https://github.com/yourusername/xiaoyuanyunbao.git
cd xiaoyuanyunbao
```

### 步骤2：创建虚拟环境
```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 步骤3：安装依赖
```
pip install -r requirements.txt
```

### 步骤4：配置环境变量
创建 `.env` 文件并配置以下内容：
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=yunbao
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 步骤5：创建数据库
```
mysql -u root -p
CREATE DATABASE yunbao CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit
```

### 步骤6：执行数据库迁移
```
python manage.py migrate
```

### 步骤7：创建超级用户
```
python manage.py createsuperuser
```

### 步骤8：启动应用
```
python manage.py runserver
```

### 步骤9：启动Celery worker
```
celery -A xiaoyuanyunbao worker -l info
```

## 5.3 典型使用流程（后端）

### 1. 用户注册流程

1. **接收注册请求**：
   ```python
   # apps/user/views.py 中的 UserRegisterView
   # 接收用户注册信息
   # 处理频率限制，防止暴力注册
   throttle_classes = [RegisterRateThrottle]
   ```

2. **验证用户输入**：
   ```python
   # 使用Django内置密码验证器
   # 确保密码符合复杂度要求
   serializer = UserRegisterSerializer(data=request.data)
   if serializer.is_valid():
       # 验证成功，继续处理
   ```

3. **创建用户账户**：
   ```python
   # 创建用户账户
   user = serializer.save()
   
   # 生成JWT令牌
   refresh = RefreshToken.for_user(user)
   ```

4. **异步任务处理**：
   ```python
   # 使用Celery异步发送欢迎邮件
   send_welcome_email.delay(user.id)
   ```

5. **安全日志记录**：
   ```python
   # 记录注册事件到安全日志
   log_registration(request, True, user.username, user=user)
   ```

6. **返回成功响应**：
   ```python
   # 返回标准格式的成功响应
   return success_response(
       data={
           "user_id": str(user.id),
           "username": user.username,
           "token": {
               "access": str(refresh.access_token),
               "refresh": str(refresh)
           }
       },
       message="注册成功",
       code=201
   )
   ```

### 2. 用户认证流程

1. **接收登录请求**：
   ```python
   # apps/user/views.py 中的 LoginView
   # 应用频率限制，防止暴力破解
   throttle_classes = [LoginRateThrottle]
   ```

2. **验证用户凭证**：
   ```python
   # 验证用户名和密码
   user = authenticate(username=username, password=password)
   ```

3. **生成访问令牌**：
   ```python
   # 为已验证用户生成JWT令牌
   refresh = RefreshToken.for_user(user)
   ```

4. **安全日志记录**：
   ```python
   # 记录登录成功/失败事件
   log_login_attempt(request, True, username, user=user)
   ```

5. **返回令牌**：
   ```python
   # 返回访问令牌和刷新令牌
   return success_response(
       data={
           "access_token": str(refresh.access_token),
           "refresh_token": str(refresh)
       },
       message="登录成功"
   )
   ```

### 3. 任务处理流程

1. **接收任务创建请求**：
   ```python
   # apps/personal_growth/views.py 中的 TaskListCreateView
   # 验证用户权限
   permission_classes = [IsAuthenticated]
   ```

2. **创建和异步处理任务**：
   ```python
   # 处理高并发场景下的任务创建
   from .tasks import create_task_plan
   task = create_task_plan.delay(request.user.id, serializer.validated_data)
   
   # 立即返回任务状态，不阻塞请求
   return success_response(
       data={
           "task_id": task.id,
           "status": "processing",
           "message": "任务正在异步创建中，可通过任务ID查询状态"
       },
       message="任务创建请求已接收",
       code=202  # 202 Accepted - 请求已接受但处理尚未完成
   )
   ```

3. **查询任务状态**：
   ```python
   # apps/personal_growth/views.py 中的 TaskStatusView
   # 获取Celery异步任务的状态和结果
   result = get_task_result(task_id)
   
   if result['status'] == 'SUCCESS':
       # 任务成功，返回任务结果
       return success_response(
           data=result['result'],
           message="任务已完成",
           code=200
       )
   elif result['status'] == 'FAILURE':
       # 任务失败，返回错误信息
       return error_response(
           message=f"任务执行失败: {result.get('error', '未知错误')}",
           code=500
       )
   else:
       # 任务仍在进行中
       return success_response(
           data={"status": result['status']},
           message="任务处理中",
           code=202
       )
   ```

### 4. 频率限制与安全保护

1. **请求频率限制**：
   ```python
   # 全局频率限制配置（settings.py）
   REST_FRAMEWORK = {
       'DEFAULT_THROTTLE_CLASSES': [
           'rest_framework.throttling.AnonRateThrottle',
           'rest_framework.throttling.UserRateThrottle',
       ],
       'DEFAULT_THROTTLE_RATES': {
           'anon': '30/minute',  # 匿名用户每分钟30次请求
           'user': '100/minute',  # 认证用户每分钟100次请求
       },
   }
   ```

2. **特定操作限制**：
   ```python
   # 登录操作频率限制
   # core/throttling.py
   class LoginRateThrottle(AnonRateThrottle):
       """
       限制登录尝试的频率
       匿名用户每分钟只能尝试5次登录
       """
       rate = '5/minute'
       scope = 'login'
   ```

3. **安全事件日志**：
   ```python
   # 记录安全事件
   # core/utils/security_utils.py
   security_logger.info(
       f"{event_type}: {message}", 
       extra={
           'user': username,
           'ip': ip,
           'path': path
       }
   )
   ```

### 5. 异步与长时间任务处理

1. **任务队列配置**：
   ```python
   # Celery任务路由配置（settings.py）
   CELERY_TASK_ROUTES = {
       'apps.user.tasks.*': {'queue': 'users'},
       'apps.life_assistant.tasks.*': {'queue': 'life_assistant'},
       'apps.virtual_study_room.tasks.*': {'queue': 'study_room'},
       'apps.personal_growth.tasks.*': {'queue': 'personal_growth'},
       'apps.campus_planning.tasks.*': {'queue': 'campus_planning'},
   }
   ```

2. **AI计划生成**：
   ```python
   # apps/personal_growth/views.py 中的 AIGeneratePlanView
   # 根据用户目标和时间范围生成学习计划
   ai_plan = AIGeneratedPlan.objects.create(
       user=request.user,
       goal_description=goal_description,
       time_range=time_range,
       current_level=current_level,
       plan_content=generated_plan
   )
   ```

3. **番茄钟会话管理**：
   ```python
   # 创建番茄钟会话
   session = serializer.save()
   
   # 更新番茄钟状态
   session.status = 'in_progress'
   session.save()
   ``` 