# 个人提升模块视图 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Plan, LearningResource, EmotionRecord, AutoTask, PomodoroSession, PomodoroRecord, AIGeneratedPlan, UserResourceFavorite
from .serializers import (
    PlanSerializer, PlanCreateSerializer, AIGeneratedPlanSerializer,
    FragmentTaskSerializer, LearningResourceSerializer, EmotionRecordSerializer,
    VoiceCommandSerializer, AutoTaskSerializer, PlanUpdateSerializer,
    PlanPauseResumeSerializer, PlanStartSerializer, PomodoroSessionCreateSerializer,
    PomodoroSessionSerializer, PomodoroSessionDetailSerializer, PomodoroSessionUpdateSerializer,
    TaskCreateSerializer, TaskSerializer, AIAnalyzePlanSerializer, EmotionAnalysisSerializer
)
from core.utils import success_response, error_response
import json
from django.utils import timezone
import datetime
from celery.result import AsyncResult
from django.conf import settings
from core.utils import get_task_result

# 尝试导入 dateutil，如果不可用，后面会使用替代方法
try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None
from .tasks import complete_task_after_time


class PlanCreateView(APIView):
    """创建新的学习计划"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PlanCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            plan = serializer.save()
            return success_response(
                data={"plan_id": plan.id},
                message="计划创建成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)


class PlanDetailView(APIView):
    """获取、更新和删除学习计划"""
    permission_classes = [IsAuthenticated]

    def get_object(self, request, **kwargs):
        # 支持 plan_id 或 task_id 参数
        plan_id = kwargs.get('plan_id') or kwargs.get('task_id')
        plan = get_object_or_404(Plan, id=plan_id, user=request.user)
        return plan

    def get(self, request, **kwargs):
        plan = self.get_object(request, **kwargs)
        serializer = PlanSerializer(plan)
        return success_response(data=serializer.data)

    def put(self, request, **kwargs):
        plan = self.get_object(request, **kwargs)
        serializer = PlanUpdateSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            plan = serializer.save()
            return success_response(
                data={"task_id": plan.id},
                message="任务更新成功"
            )
        return error_response(message=serializer.errors, code=400)


class PlanPauseResumeView(APIView):
    """暂停或重启学习计划"""
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id, user=request.user)
        serializer = PlanPauseResumeSerializer(data=request.data)

        if serializer.is_valid():
            action = serializer.validated_data['action']

            if action == 'pause':
                plan.status = 'paused'
                message = "计划已暂停"
            elif action == 'resume':
                plan.status = 'active'
                message = "计划已重启"

            plan.save()

            return success_response(
                data={
                    "plan_id": plan_id,
                    "status": plan.status
                },
                message=message
            )
        return error_response(message=serializer.errors, code=400)


class EmotionHistoryView(APIView):
    """获取情绪历史记录"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        emotion_records = EmotionRecord.objects.filter(user=request.user).order_by('-created_at')
        history = []

        for record in emotion_records:
            history.append({
                "timestamp": record.created_at.isoformat(),
                "emotion_detected": record.emotion,
                "adjustment_suggestions": record.adjustment_suggestion
            })

        return success_response(data={"history": history}, message="获取情绪历史成功")


# 任务处理视图
class FragmentTaskView(APIView):
    """任务碎片化"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """测试接口，返回简单成功消息"""
        return success_response(
            data={"message": "FragmentTaskView GET方法测试成功"},
            message="接口可用",
            code=200
        )

    def post(self, request):
        """将指定任务拆解为微任务"""
        print("FragmentTaskView收到POST请求:", request.data)
        
        serializer = FragmentTaskSerializer(data=request.data)
        if serializer.is_valid():
            print("验证通过:", serializer.validated_data)
            task_id = serializer.validated_data['task_id']
            fragment_time = serializer.validated_data['fragment_time']

            # 获取原任务 - 修改为支持字符串ID
            try:
                # 先尝试将task_id转为整数查询
                numeric_id = None
                try:
                    numeric_id = int(task_id)
                except (ValueError, TypeError):
                    pass
                
                if numeric_id is not None:
                    original_task = get_object_or_404(Plan, id=numeric_id, user=request.user)
                else:
                    # 如果转换失败，按原始格式查询
                    # 注意：这里假设ID可能是字符串格式，需要数据库字段支持
                    original_task = Plan.objects.filter(user=request.user).first()
                    if not original_task:
                        return error_response(message="任务不存在", code=404)
            except Plan.DoesNotExist:
                return error_response(message="任务不存在", code=404)

            # 计算需要拆分的碎片数量
            total_fragments = max(1, int(original_task.focus_time / fragment_time))

            # 创建碎片任务
            fragment_tasks = []
            for i in range(total_fragments):
                # 限制任务名称长度，确保不超过数据库列限制（假设最大为50个字符）
                base_name = original_task.task_name
                if len(base_name) > 40:  # 预留10个字符给碎片标识
                    base_name = base_name[:37] + "..."
                
                fragment_name = f"{base_name}（碎片{i + 1}）"
                fragment_task = Plan.objects.create(
                    user=request.user,
                    task_name=fragment_name,
                    focus_time=fragment_time,
                    rest_time=original_task.rest_time,
                    scheduled_date=original_task.scheduled_date
                )
                fragment_tasks.append(fragment_task)

            # 序列化结果
            serializer = PlanSerializer(fragment_tasks, many=True)
            return success_response(
                data=serializer.data,
                message="任务碎片化成功",
                code=201
            )
        else:
            print("验证失败:", serializer.errors)
        return error_response(message=serializer.errors, code=400)


# 资源管理视图
class ResourceRecommendView(APIView):
    """自动推荐学习资源"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """根据当前任务推荐适合碎片化学习的短时资源"""
        current_task = request.query_params.get('current_task', '')
        
        # 如果没有提供current_task，使用默认值
        if not current_task:
            current_task = "通用学习"

        # 这里应该根据任务名称查询或生成推荐资源
        # 为了演示，我们生成一些示例资源
        resources = [
            {
                "title": f"5分钟{current_task}微课",
                "duration": "5分钟",
                "url": f"http://example.com/{current_task.replace(' ', '-')}-micro-lesson"
            },
            {
                "title": f"{current_task}快速入门",
                "duration": "10分钟",
                "url": f"http://example.com/{current_task.replace(' ', '-')}-quick-start"
            },
            {
                "title": f"{current_task}核心概念",
                "duration": "15分钟",
                "url": f"http://example.com/{current_task.replace(' ', '-')}-core-concepts"
            }
        ]

        return success_response(
            data={"resources_list": resources},
            message="资源推荐成功"
        )


class ResourceFavoriteView(APIView):
    """收藏学习资源"""
    permission_classes = [IsAuthenticated]

    def post(self, request, resource_id):
        """用户收藏推荐的学习资源"""
        # 查找资源
        try:
            # 先尝试将resource_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(resource_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                resource = LearningResource.objects.get(id=numeric_id)
            else:
                # 如果不是数字ID，则使用第一个资源（演示用）
                resource = LearningResource.objects.first()
                if not resource:
                    return error_response(message="资源不存在", code=404)
        except LearningResource.DoesNotExist:
            return error_response(message="资源不存在", code=404)

        # 添加到用户收藏
        favorite, created = UserResourceFavorite.objects.get_or_create(
            user=request.user,
            resource=resource
        )

        return success_response(
            data={
                "resource_id": str(resource_id),
                "favorited": True
            },
            message="收藏成功"
        )


class EmotionAnalysisView(APIView):
    """情绪分析视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """分析用户情绪"""
        # 支持两种请求格式：voice_text 或 EmotionAnalysisSerializer 的 text 字段
        voice_text = request.data.get('voice_text', '')
        text = request.data.get('text', '')
        
        # 使用提供的任一文本内容
        input_text = voice_text or text
        
        # 如果没有提供任何文本内容，使用默认响应
        if not input_text:
            return success_response(
                data={
                    "emotion": "neutral",
                    "suggestions": ["您好，有什么可以帮助您的吗？"],
                    "score": 0.5
                },
                message="情绪分析完成"
            )

        # 如果使用 EmotionAnalysisSerializer 格式
        if text:
            serializer = EmotionAnalysisSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                emotion_record = serializer.save()
                return success_response(
                    data={
                        "emotion": emotion_record.emotion,
                        "suggestions": [emotion_record.adjustment_suggestion],
                        "score": 0.8  # 示例分数
                    },
                    message="情绪分析完成"
                )
            return error_response(message=serializer.errors, code=400)
            
        # 使用 voice_text 格式（原有逻辑）
        # 这里应该接入实际的情绪分析API
        # 为了演示，我们模拟一个简单的情绪分析结果
        import random
        emotions = ["happy", "sad", "anxious", "excited", "tired", "neutral"]
        emotion = random.choice(emotions)
        
        suggestions = {
            "happy": ["继续保持这种好心情！", "这是开始新任务的好时机"],
            "sad": ["听些轻松的音乐可能会有帮助", "考虑短暂休息一下"],
            "anxious": ["深呼吸可以帮助缓解焦虑", "试着将任务分解成更小的步骤"],
            "excited": ["将这种能量用于你最重要的任务", "设定一个挑战性目标"],
            "tired": ["考虑小睡一会儿", "喝点水，做些伸展运动"],
            "neutral": ["当前是专注工作的好状态", "考虑安排一些创造性任务"]
        }
        
        return success_response(
            data={
                "emotion": emotion,
                "suggestions": suggestions[emotion],
                "score": random.uniform(0.6, 0.9)
            },
            message="情绪分析完成"
        )


class VoiceAssistantView(APIView):
    """语音助手控制任务"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        voice_command = request.data.get('voice_command')
        if not voice_command:
            return error_response(message="缺少语音指令", code=400)

        serializer = VoiceCommandSerializer(data={'command': voice_command}, context={'request': request})
        if serializer.is_valid():
            voice_record = serializer.save()
            return success_response(
                data={"execution_result": voice_record.execution_result},
                message="指令执行成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)


class PlanStartView(APIView):
    """启动学习计划"""
    permission_classes = [IsAuthenticated]

    def post(self, request, plan_id):
        try:
            # 先尝试将plan_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(plan_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                plan = Plan.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认选择第一个计划（演示用）
                plan = Plan.objects.filter(user=request.user).first()
                if not plan:
                    return error_response(message="计划不存在", code=404)

            # 检查计划是否已经启动或已完成
            if plan.status == 'active':
                return error_response(message="计划已经启动", code=409)
            elif plan.status == 'completed':
                return error_response(message="计划已经完成", code=409)

            serializer = PlanStartSerializer(data=request.data)
            if serializer.is_valid():
                # 获取开始时间，如果未提供则使用当前时间
                start_time = serializer.validated_data.get('start_time', timezone.now())

                # 更新计划状态
                plan.status = 'active'
                plan.start_time = start_time
                plan.save()

                return success_response(
                    data={
                        "task_id": str(plan_id),
                        "status": plan.status,
                        "start_time": plan.start_time.isoformat()
                    },
                    message="计划启动成功",
                    code=200
                )
            return error_response(message=serializer.errors, code=400)
        except Plan.DoesNotExist:
            return error_response(message="计划不存在", code=404)


# 任务管理视图
class TaskListCreateView(APIView):
    """创建和获取任务列表"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """创建任务计划（含存钱计划）- 使用Celery异步处理高并发"""
        # 使用新的符合API文档的序列化器
        serializer = TaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 高并发模式：将任务创建委派给Celery异步处理
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
            
            # 原先的同步模式代码注释掉以作对比：
            # plan = serializer.save()
            # return success_response(
            #     data={
            #         "task_id": str(plan.id),
            #         "title": plan.task_name,
            #         "status": plan.status,
            #         "created_at": plan.created_at.isoformat()
            #     },
            #     message="任务创建成功",
            #     code=201
            # )
        return error_response(message=serializer.errors, code=400)

    def get(self, request):
        """获取任务列表"""
        # 获取查询参数
        date_str = request.query_params.get('date')
        granularity = request.query_params.get('granularity', 'day')

        # 处理日期参数
        if date_str:
            try:
                query_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return error_response(message="日期格式错误，应为YYYY-MM-DD", code=400)
        else:
            query_date = timezone.now().date()

        # 根据粒度查询任务
        if granularity == 'day':
            plans = Plan.objects.filter(user=request.user, scheduled_date=query_date)
        elif granularity == 'week':
            # 计算本周的开始和结束日期
            today = query_date
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            plans = Plan.objects.filter(
                user=request.user,
                scheduled_date__gte=start_of_week,
                scheduled_date__lte=end_of_week
            )
        elif granularity == 'long-term':
            # 查询所有未来的计划
            plans = Plan.objects.filter(
                user=request.user,
                scheduled_date__gte=query_date
            )
        else:
            return error_response(message="不支持的时间粒度，应为day/week/long-term", code=400)

        # 使用符合API文档的序列化器
        serializer = TaskSerializer(plans, many=True)
        return success_response(data={"tasks": serializer.data})


class TaskDetailView(APIView):
    """获取和更新任务详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        """获取任务详情"""
        plan = get_object_or_404(Plan, id=task_id, user=request.user)
        serializer = TaskSerializer(plan)
        return success_response(data=serializer.data)

    def put(self, request, task_id):
        """更新任务"""
        plan = get_object_or_404(Plan, id=task_id, user=request.user)
        # 转换请求数据格式
        converted_data = {}
        if 'title' in request.data:
            converted_data['task_name'] = request.data['title']
        if 'estimated_time' in request.data:
            converted_data['focus_time'] = request.data['estimated_time']
        if 'due_date' in request.data:
            due_date = request.data['due_date']
            # 如果 due_date 是 datetime 字符串，转换为 date
            if isinstance(due_date, str) and 'T' in due_date:
                try:
                    # 尝试解析 ISO 格式的 datetime 字符串
                    if date_parser:
                        due_date = date_parser.parse(due_date).date()
                    else:
                        # 如果 dateutil 不可用，使用简单的方法
                        due_date = due_date.split('T')[0]
                except ValueError:
                    # 如果解析失败，使用简单的方法
                    due_date = due_date.split('T')[0]
            converted_data['scheduled_date'] = due_date
        if 'status' in request.data:
            converted_data['status'] = request.data['status']

        serializer = PlanUpdateSerializer(plan, data=converted_data, partial=True)
        if serializer.is_valid():
            plan = serializer.save()
            # 返回符合API文档格式的响应
            return success_response(
                data={
                    "task_id": str(task_id),
                    "title": plan.task_name,
                    "status": plan.status
                },
                message="任务更新成功"
            )
        return error_response(message=serializer.errors, code=400)

    def delete(self, request, task_id):
        """删除任务"""
        try:
            plan = get_object_or_404(Plan, id=task_id, user=request.user)
            task_name = plan.task_name  # 保存任务名称以便在响应中使用

            # 使用原始SQL删除，避免关联关系检查
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM personal_growth_plan WHERE id = %s", [task_id])

            return success_response(
                data={
                    "task_id": task_id,
                    "message": f"任务 '{task_name}' 已删除"
                },
                message="任务删除成功",
                code=200
            )
        except Exception as e:
            return error_response(
                message=f"删除任务时出错: {str(e)}",
                code=500
            )


class TaskStartSerializer(serializers.Serializer):
    """启动任务计时序列化器"""
    start_time = serializers.DateTimeField(required=False)


class TaskStartView(APIView):
    """开始任务计时"""
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        """启动指定任务的计时"""
        try:
            # 先尝试将task_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(task_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                task = Plan.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认选择第一个任务（演示用）
                task = Plan.objects.filter(user=request.user).first()
                if not task:
                    return error_response(message="任务不存在", code=404)

            # 检查任务状态
            if task.status == 'active':
                return error_response(message="任务已启动", code=409)
            elif task.status == 'completed':
                return error_response(message="任务已完成", code=409)

            # 获取开始时间
            serializer = TaskStartSerializer(data=request.data)
            if serializer.is_valid():
                start_time = serializer.validated_data.get('start_time', timezone.now())
                
                # 更新任务状态
                task.status = 'active'
                task.start_time = start_time
                task.save()
                
                return success_response(
                    data={
                        "task_id": str(task_id),
                        "status": "active",
                        "start_time": start_time.isoformat()
                    },
                    message="计时启动成功", 
                    code=200
                )
            return error_response(message=serializer.errors, code=400)
        except Plan.DoesNotExist:
            return error_response(message="任务不存在", code=404)


class TaskPauseView(APIView):
    """暂停或重启任务"""
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        """暂停或重启指定任务的计时"""
        try:
            # 先尝试将task_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(task_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                task = Plan.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认选择第一个任务（演示用）
                task = Plan.objects.filter(user=request.user).first()
                if not task:
                    return error_response(message="任务不存在", code=404)

            # 验证操作
            serializer = PlanPauseResumeSerializer(data=request.data)
            if serializer.is_valid():
                action = serializer.validated_data['action']
                
                # 暂停任务
                if action == 'pause':
                    if task.status != 'active':
                        return error_response(message="任务未处于活动状态，无法暂停", code=400)
                    task.status = 'paused'
                
                # 重启任务
                elif action == 'resume':
                    if task.status != 'paused':
                        return error_response(message="任务未处于暂停状态，无法重启", code=400)
                    task.status = 'active'
                
                task.save()
                
                return success_response(
                    data={
                        "task_id": str(task_id),
                        "status": task.status
                    },
                    message="操作成功",
                    code=200
                )
            return error_response(message=serializer.errors, code=400)
        except Plan.DoesNotExist:
            return error_response(message="任务不存在", code=404)


# AI 计划视图
class AIGeneratePlanView(APIView):
    """AI 生成学习计划"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """根据目标和时间范围生成结构化计划"""
        print(f"AIGeneratePlanView received data: {request.data}")
        
        # 验证用户是否已认证，若未认证则允许演示模式
        if not request.user.is_authenticated:
            print("User is not authenticated, using demo mode")
            # 演示模式：生成一个简单的计划
            demo_data = {
                "goal_description": request.data.get('goal_description', "示例目标"),
                "time_range": request.data.get('time_range', "2025-03-17至2025-06-17"),
                "granularity": request.data.get('granularity', 'day'),
                "current_level": request.data.get('current_level', '初学者')
            }
            # 使用演示数据创建序列化器
            serializer = AIGeneratedPlanSerializer(data=demo_data)
        else:
            serializer = AIGeneratedPlanSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            print(f"Serializer is valid: {serializer.validated_data}")
            goal_description = serializer.validated_data['goal_description']
            time_range = serializer.validated_data['time_range']
            granularity = serializer.validated_data.get('granularity', 'week')
            current_level = serializer.validated_data.get('current_level', '')

            # 解析时间范围
            try:
                start_date, end_date = time_range.split('至')
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                print(f"Error parsing time range: {time_range}")
                return error_response(message="时间范围格式错误，应为'YYYY-MM-DD至YYYY-MM-DD'", code=400)

            # 这里应该调用 AI 服务生成计划
            # 为了演示，我们生成一个简单的示例计划
            generated_plan = {}
            current_date = start_date
            while current_date <= end_date:
                if granularity == 'day' or (granularity == 'week' and current_date.weekday() == 0):
                    date_str = current_date.strftime('%Y-%m-%d')
                    generated_plan[date_str] = [
                        {
                            "task_name": f"学习任务 {(current_date - start_date).days + 1}",
                            "focus_time": 25,
                            "rest_time": 5,
                            "savings_amount": 2.0
                        }
                    ]
                current_date += datetime.timedelta(days=1)

            # 创建并保存AI生成计划到数据库
            if request.user.is_authenticated:
                ai_plan = AIGeneratedPlan.objects.create(
                    user=request.user,
                    goal_description=goal_description,
                    time_range=time_range,
                    current_level=current_level,
                    plan_content=generated_plan
                )
                plan_id = str(ai_plan.id)
            else:
                # 演示模式下使用临时ID
                plan_id = "demo-plan-1"

            return success_response(
                data={
                    "plan_id": plan_id,
                    "generated_plan": generated_plan
                },
                message="计划生成成功",
                code=201
            )
        else:
            print(f"Serializer errors: {serializer.errors}")
            return error_response(message=serializer.errors, code=400)


class AIPlanDetailView(APIView):
    """AI生成计划详情视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, plan_id):
        """获取AI生成的学习计划详情"""
        try:
            # 先尝试将plan_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(plan_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                plan = AIGeneratedPlan.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认选择第一个计划（演示用）
                plan = AIGeneratedPlan.objects.filter(user=request.user).first()
                if not plan:
                    return error_response(message="学习计划不存在", code=404)
            
            # 返回计划详情
            return success_response(
                data={
                    "plan_id": str(plan_id),
                    "goal_description": plan.goal_description,
                    "time_range": plan.time_range,
                    "current_level": plan.current_level,
                    "plan_content": plan.plan_content,
                    "created_at": plan.created_at.isoformat()
                },
                message="获取成功",
                code=200
            )
        except AIGeneratedPlan.DoesNotExist:
            return error_response(message="学习计划不存在", code=404)

    def put(self, request, plan_id):
        """更新AI生成的学习计划"""
        try:
            # 先尝试将plan_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(plan_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                plan = AIGeneratedPlan.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认选择第一个计划（演示用）
                plan = AIGeneratedPlan.objects.filter(user=request.user).first()
                if not plan:
                    return error_response(message="学习计划不存在", code=404)
            
            # 只更新请求中包含的字段
            if 'goal_description' in request.data:
                plan.goal_description = request.data['goal_description']
            
            if 'time_range' in request.data:
                plan.time_range = request.data['time_range']
            
            if 'current_level' in request.data:
                plan.current_level = request.data['current_level']
            
            if 'plan_content' in request.data:
                plan.plan_content = request.data['plan_content']
            
            # 保存更新后的计划
            plan.save()
            
            return success_response(
                data={
                    "plan_id": str(plan_id),
                    "goal_description": plan.goal_description,
                    "time_range": plan.time_range,
                    "current_level": plan.current_level,
                    "plan_content": plan.plan_content,
                    "updated_at": timezone.now().isoformat()
                },
                message="学习计划更新成功",
                code=200
            )
        except AIGeneratedPlan.DoesNotExist:
            return error_response(message="学习计划不存在", code=404)

    def delete(self, request, plan_id):
        """删除AI生成的学习计划"""
        try:
            # 先尝试将plan_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(plan_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                plan = AIGeneratedPlan.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认选择第一个计划（演示用）
                plan = AIGeneratedPlan.objects.filter(user=request.user).first()
                if not plan:
                    return error_response(message="学习计划不存在", code=404)
            
            # 删除计划
            plan.delete()
            
            return success_response(
                message="学习计划删除成功",
                code=200
            )
        except AIGeneratedPlan.DoesNotExist:
            return error_response(message="学习计划不存在", code=404)


class AIAnalyzePlanView(APIView):
    """分析单独输入的计划"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """解析文本计划，生成任务板块并分配到日期/周"""
        serializer = AIAnalyzePlanSerializer(data=request.data)
        if serializer.is_valid():
            plan_text = serializer.validated_data['plan_text']
            granularity = serializer.validated_data.get('granularity', 'day')

            # 这里应该调用 AI 服务解析计划文本
            # 为了演示，我们生成一个简单的示例计划
            today = timezone.now().date()
            generated_plan = {}

            # 简单解析示例：假设文本中包含"每天"或"每周"等关键词
            if "每天" in plan_text:
                for i in range(7):  # 生成一周的计划
                    date = today + datetime.timedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    generated_plan[date_str] = [
                        {
                            "task_name": "每日任务",
                            "focus_time": 30,
                            "rest_time": 5
                        }
                    ]
            elif "每周" in plan_text:
                # 生成本周的计划
                start_of_week = today - datetime.timedelta(days=today.weekday())
                for i in range(7):
                    date = start_of_week + datetime.timedelta(days=i)
                    if i < 5:  # 工作日
                        date_str = date.strftime('%Y-%m-%d')
                        generated_plan[date_str] = [
                            {
                                "task_name": "工作日任务",
                                "focus_time": 45,
                                "rest_time": 10
                            }
                        ]
            else:
                # 默认生成今天的计划
                date_str = today.strftime('%Y-%m-%d')
                generated_plan[date_str] = [
                    {
                        "task_name": "默认任务",
                        "focus_time": 25,
                        "rest_time": 5
                    }
                ]

            return success_response(
                data={"generated_plan": generated_plan},
                message="计划解析成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)


# 自动化任务视图
class AutoTaskView(APIView):
    """设置自动执行任务"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取自动执行任务列表"""
        auto_tasks = AutoTask.objects.filter(user=request.user)
        tasks_data = []
        
        for task in auto_tasks:
            tasks_data.append({
                "task_id": str(task.id),
                "task_description": task.task_description,
                "execution_time": task.execution_time,
                "is_active": task.is_active,
                "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None
            })
        
        return success_response(
            data={"auto_tasks": tasks_data},
            message="获取自动任务列表成功"
        )

    def post(self, request):
        """开启自动模式，到指定时间自动开始任务"""
        print(f"AutoTaskView received POST data: {request.data}")
        
        # 检查必要字段
        if 'task_plan' not in request.data or 'auto_execute_switch' not in request.data:
            return error_response(
                message="缺少必要字段: task_plan 和 auto_execute_switch 是必需的",
                code=400
            )
            
        serializer = AutoTaskSerializer(data=request.data)
        if serializer.is_valid():
            print(f"AutoTaskSerializer validation successful: {serializer.validated_data}")
            task_plan = serializer.validated_data['task_plan']
            auto_execute_switch = serializer.validated_data['auto_execute_switch']
            reminder_minutes = serializer.validated_data.get('reminder_minutes', 5)
            scheduled_date = serializer.validated_data.get('scheduled_date', timezone.now().date())

            # 创建自动任务
            auto_task = AutoTask.objects.create(
                user=request.user,
                task_description=task_plan.get('task', ''),
                execution_time=task_plan.get('time', ''),
                is_active=auto_execute_switch,
                reminder_minutes=reminder_minutes,
                scheduled_date=scheduled_date
            )

            return success_response(
                data={
                    "task_id": str(auto_task.id),
                    "message": "自动任务已设置"
                },
                message="设置成功",
                code=201
            )
        else:
            print(f"AutoTaskSerializer validation failed: {serializer.errors}")
            return error_response(message=serializer.errors, code=400)


class AutoTaskCancelView(APIView):
    """取消自动执行任务"""
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        """取消自动执行任务"""
        try:
            # 先尝试将task_id转为整数查询
            numeric_id = None
            try:
                numeric_id = int(task_id)
            except (ValueError, TypeError):
                pass
            
            if numeric_id is not None:
                auto_task = AutoTask.objects.get(id=numeric_id, user=request.user)
            else:
                # 如果不是数字ID，默认取消第一个任务（演示用）
                auto_task = AutoTask.objects.filter(user=request.user).first()
                if not auto_task:
                    return error_response(message="任务不存在", code=404)
                
            # 停用任务
            auto_task.is_active = False
            auto_task.save()
            
            return success_response(
                data={
                    "task_id": str(task_id),
                    "auto_execute_switch": False
                },
                message="自动执行任务已取消",
                code=200
            )
        except AutoTask.DoesNotExist:
            return error_response(message="任务不存在", code=404)


# 番茄钟会话视图
class PomodoroSessionListCreateView(APIView):
    """番茄钟会话列表和创建视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """创建新的番茄钟会话"""
        serializer = PomodoroSessionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            session = serializer.save()
            return success_response(
                data={
                    "session_id": str(session.id),
                    "title": session.title,
                    "status": session.status,
                    "created_at": session.created_at
                },
                message="番茄钟会话创建成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

    def get(self, request):
        """获取用户的番茄钟会话列表"""
        # 获取查询参数
        status = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # 基本查询条件
        query_params = {'user': request.user}

        # 添加状态过滤
        if status:
            query_params['status'] = status

        # 添加日期过滤
        if start_date:
            try:
                start_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d').replace(
                    hour=0, minute=0, second=0
                )
                query_params['created_at__gte'] = start_datetime
            except ValueError:
                return error_response(message="开始日期格式错误，应为YYYY-MM-DD", code=400)

        if end_date:
            try:
                end_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d').replace(
                    hour=23, minute=59, second=59
                )
                query_params['created_at__lte'] = end_datetime
            except ValueError:
                return error_response(message="结束日期格式错误，应为YYYY-MM-DD", code=400)

        # 查询会话列表
        sessions = PomodoroSession.objects.filter(**query_params)
        serializer = PomodoroSessionSerializer(sessions, many=True)

        return success_response(
            data={
                "sessions": serializer.data,
                "total": sessions.count()
            }
        )


class PomodoroSessionDetailView(APIView):
    """番茄钟会话详情、更新和删除视图"""
    permission_classes = [IsAuthenticated]

    def get_object(self, session_id, user):
        """获取指定的番茄钟会话"""
        try:
            return PomodoroSession.objects.get(id=session_id, user=user)
        except PomodoroSession.DoesNotExist:
            raise Http404("番茄钟会话不存在")

    def get(self, request, session_id):
        """获取番茄钟会话详情"""
        session = self.get_object(session_id, request.user)
        serializer = PomodoroSessionDetailSerializer(session)
        return success_response(data=serializer.data)

    def put(self, request, session_id):
        """更新番茄钟会话状态"""
        session = self.get_object(session_id, request.user)
        serializer = PomodoroSessionUpdateSerializer(data=request.data)

        if serializer.is_valid():
            action = serializer.validated_data['action']
            current_pomodoro = serializer.validated_data.get('current_pomodoro')
            notes = serializer.validated_data.get('notes', '')

            now = timezone.now()

            # 根据不同的操作更新会话状态
            if action == 'start':
                if session.status in ['in_progress']:
                    return error_response(message="会话已经开始", code=400)

                session.status = 'in_progress'

                # 创建新的番茄钟记录
                if current_pomodoro:
                    pomodoro_number = current_pomodoro
                else:
                    pomodoro_number = session.completed_pomodoros + 1

                # 检查是否已存在该序号的记录
                record, created = PomodoroRecord.objects.get_or_create(
                    session=session,
                    pomodoro_number=pomodoro_number,
                    defaults={'start_time': now}
                )

                if not created:
                    # 如果记录已存在但未完成，更新开始时间
                    if not record.is_completed:
                        record.start_time = now
                        record.save()

                # 计算下一阶段
                if pomodoro_number % session.long_break_interval == 0:
                    next_phase = 'long_break'
                    remaining_seconds = session.long_break_minutes * 60
                else:
                    next_phase = 'focus'
                    remaining_seconds = session.focus_minutes * 60

                return success_response(
                    data={
                        "session_id": str(session.id),
                        "status": session.status,
                        "current_pomodoro": pomodoro_number,
                        "next_phase": next_phase,
                        "remaining_seconds": remaining_seconds,
                        "updated_at": now.isoformat()
                    },
                    message="番茄钟开始"
                )

            elif action == 'pause':
                if session.status != 'in_progress':
                    return error_response(message="会话未在进行中，无法暂停", code=400)

                session.status = 'paused'

                # 处理当前番茄钟记录
                if current_pomodoro:
                    try:
                        record = PomodoroRecord.objects.get(
                            session=session,
                            pomodoro_number=current_pomodoro,
                            is_completed=False
                        )
                        # 计算已经过去的时间
                        elapsed_time = (now - record.start_time).total_seconds()
                        remaining_seconds = (session.focus_minutes * 60) - elapsed_time

                        return success_response(
                            data={
                                "session_id": str(session.id),
                                "status": session.status,
                                "remaining_seconds": max(0, remaining_seconds),
                                "updated_at": now.isoformat()
                            },
                            message="番茄钟已暂停"
                        )
                    except PomodoroRecord.DoesNotExist:
                        pass

                return success_response(
                    data={
                        "session_id": str(session.id),
                        "status": session.status,
                        "updated_at": now.isoformat()
                    },
                    message="番茄钟已暂停"
                )

            elif action == 'resume':
                if session.status != 'paused':
                    return error_response(message="会话未暂停，无法恢复", code=400)

                session.status = 'in_progress'

                # 如果提供了当前番茄钟序号，尝试获取和更新记录
                remaining_seconds = session.focus_minutes * 60
                if current_pomodoro:
                    try:
                        record = PomodoroRecord.objects.get(
                            session=session,
                            pomodoro_number=current_pomodoro,
                            is_completed=False
                        )
                        # 计算剩余时间（这里简化处理，实际应用可能需要保存暂停时的剩余时间）
                        elapsed_time = (record.start_time - now).total_seconds()
                        remaining_seconds = (session.focus_minutes * 60) - elapsed_time
                    except PomodoroRecord.DoesNotExist:
                        pass

                return success_response(
                    data={
                        "session_id": str(session.id),
                        "status": session.status,
                        "remaining_seconds": max(0, remaining_seconds),
                        "updated_at": now.isoformat()
                    },
                    message="番茄钟已恢复"
                )

            elif action == 'complete':
                # 完成当前番茄钟
                if current_pomodoro:
                    try:
                        record = PomodoroRecord.objects.get(
                            session=session,
                            pomodoro_number=current_pomodoro,
                            is_completed=False
                        )
                        record.end_time = now
                        record.is_completed = True
                        record.notes = notes

                        # 计算实际持续时间（分钟）
                        duration_seconds = (now - record.start_time).total_seconds()
                        record.actual_duration = int(duration_seconds / 60)
                        record.save()

                        # 更新会话的番茄钟完成数和总专注时间
                        session.completed_pomodoros += 1
                        session.total_focus_time += record.actual_duration

                        # 如果所有计划的番茄钟都已完成，标记会话为已完成
                        if session.planned_pomodoros > 0 and session.completed_pomodoros >= session.planned_pomodoros:
                            session.status = 'completed'
                            session.completed_at = now
                    except PomodoroRecord.DoesNotExist:
                        pass

                # 如果没有指定current_pomodoro或找不到记录，仍然可以手动标记会话完成
                if action == 'complete' and not current_pomodoro:
                    session.status = 'completed'
                    session.completed_at = now

                # 更新用户的总专注时间
                if session.user.total_focus_time is not None:
                    session.user.total_focus_time += session.total_focus_time
                    session.user.save()

                # 如果关联了任务，也更新任务的已完成时间
                if session.task:
                    session.task.completed_focus_time += session.total_focus_time

                    # 如果设置了存钱金额，更新已解锁金额
                    if session.task.savings_amount:
                        completion_ratio = min(session.task.completed_focus_time / session.task.focus_time, 1.0)
                        session.task.unlocked_savings = session.task.savings_amount * completion_ratio

                    # 如果任务时间已经完成，更新任务状态
                    if session.task.completed_focus_time >= session.task.focus_time:
                        session.task.status = 'completed'

                    session.task.save()

                return success_response(
                    data={
                        "session_id": str(session.id),
                        "status": session.status,
                        "completed_pomodoros": session.completed_pomodoros,
                        "total_focus_time": session.total_focus_time,
                        "updated_at": now.isoformat()
                    },
                    message="番茄钟已完成"
                )

            elif action == 'cancel':
                # 取消会话
                session.status = 'completed'  # 使用已完成状态表示取消
                session.completed_at = now

                return success_response(
                    data={
                        "session_id": str(session.id),
                        "status": session.status,
                        "updated_at": now.isoformat()
                    },
                    message="番茄钟已取消"
                )

            # 保存会话状态
            session.save()

            return success_response(
                data={
                    "session_id": str(session.id),
                    "status": session.status,
                    "updated_at": now.isoformat()
                },
                message="番茄钟状态已更新"
            )

        return error_response(message=serializer.errors, code=400)


class TestAIGeneratePlanView(APIView):
    """测试用AI生成学习计划视图，不需要认证"""
    permission_classes = []  # 无需认证

    def post(self, request):
        """用于测试的AI生成计划接口"""
        print(f"TestAIGeneratePlanView received data: {request.data}")

        serializer = AIGeneratedPlanSerializer(data=request.data)
        if serializer.is_valid():
            print(f"Test serializer valid with data: {serializer.validated_data}")
            goal_description = serializer.validated_data['goal_description']
            time_range = serializer.validated_data['time_range']
            return success_response(
                data={
                    "plan_id": "test-plan-id",
                    "goal_description": goal_description,
                    "time_range": time_range,
                    "test_mode": True
                }, 
                message="测试成功", 
                code=200
            )
        else:
            print(f"Test serializer errors: {serializer.errors}")
            return error_response(message=serializer.errors, code=400)


class TaskStatusView(APIView):
    """获取任务创建状态"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        """
        获取Celery异步任务的状态和结果
        """
        # 获取任务状态
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


class TaskRecommendView(APIView):
    """推荐任务相关资源"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """获取关于特定任务的推荐资源"""
        try:
            task = get_object_or_404(Plan, id=pk, user=request.user)
            
            # 这里应该根据任务内容生成推荐
            # 为了演示，我们生成一些示例推荐
            recommendations = [
                {
                    "title": f"关于{task.task_name}的学习资料",
                    "type": "article",
                    "url": f"https://example.com/articles/{pk}"
                },
                {
                    "title": f"{task.task_name}最佳实践",
                    "type": "video",
                    "url": f"https://example.com/videos/{pk}"
                },
                {
                    "title": f"{task.task_name}专题讨论",
                    "type": "forum",
                    "url": f"https://example.com/forums/{pk}"
                }
            ]
            
            return success_response(
                data={"recommendations": recommendations},
                message="获取推荐成功"
            )
        except Plan.DoesNotExist:
            return error_response(message="任务不存在", code=404)
