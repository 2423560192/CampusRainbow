# 个人提升模块视图 
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Plan, LearningResource, EmotionRecord, AutoTask
from .serializers import (
    PlanSerializer, PlanCreateSerializer, AIGeneratedPlanSerializer,
    FragmentTaskSerializer, LearningResourceSerializer, EmotionRecordSerializer,
    VoiceCommandSerializer, AutoTaskSerializer, PlanUpdateSerializer,
    PlanPauseResumeSerializer, PlanStartSerializer
)
from core.utils import success_response, error_response
import json
from django.utils import timezone
import datetime

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

class AIGeneratePlanView(APIView):
    """AI 生成学习计划"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AIGeneratedPlanSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 这里可以添加调用AI生成计划的逻辑
            goal = serializer.validated_data['goal_description']
            time_range = serializer.validated_data['time_range']
            
            # 模拟AI生成的计划内容
            generated_plan = self._generate_plan(goal, time_range)
            
            # 保存生成的计划
            serializer.validated_data['plan_content'] = generated_plan
            ai_plan = serializer.save()
            
            return success_response(
                data={"generated_plan": generated_plan},
                message="学习计划生成成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)
    
    def _generate_plan(self, goal, time_range):
        """模拟AI生成学习计划"""
        if "四级" in goal:
            return {
                "week1": "每天背50个单词，听力练习30分钟",
                "week2": "每天背50个单词，阅读练习30分钟",
                "week3": "每天背50个单词，写作练习30分钟",
                "week4": "每天背50个单词，口语练习30分钟",
                "week5": "每天做一套真题，分析错题",
                "week6": "每天做一套真题，强化弱项",
                "week7": "全面复习，模拟考试",
                "week8": "查漏补缺，调整状态",
                "week9": "最后冲刺，考前准备",
                "week10": "放松心态，以最佳状态迎接考试",
                "tips": "坚持每天学习，保持良好作息，考前一周不要熬夜"
            }
        elif "考研" in goal:
            return {
                "month1": "制定详细的复习计划，熟悉考试大纲",
                "month2": "专业课基础知识学习，每天背诵英语单词",
                "month3": "专业课深入学习，政治基础学习",
                "tips": "建议每天保持6-8小时的学习时间，周末可以适当增加"
            }
        else:
            return {
                "phase1": "了解目标和要求",
                "phase2": "制定详细学习计划",
                "phase3": "每日坚持学习",
                "phase4": "定期复习和测试",
                "phase5": "总结经验，调整计划",
                "tips": "保持积极心态，合理安排时间"
            }

class TaskFragmentView(APIView):
    """碎片化任务拆解"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FragmentTaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # 这里可以添加任务拆解逻辑
            parent_task = serializer.validated_data['parent_task']
            fragment_time = serializer.validated_data['fragment_time']
            
            # 模拟拆解任务
            micro_tasks = self._fragment_task(parent_task, fragment_time)
            
            # 保存拆解结果
            serializer.validated_data['micro_tasks'] = micro_tasks
            fragment = serializer.save()
            
            return success_response(
                data={"micro_tasks": micro_tasks},
                message="任务拆解成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)
    
    def _fragment_task(self, task_goal, fragment_time):
        """拆解任务为微任务"""
        if "背单词" in task_goal:
            # 根据碎片时间拆分任务
            if fragment_time <= 5:
                return ["背5个单词", "复习前一天的5个单词"]
            elif fragment_time <= 10:
                return ["背10个单词", "复习前一天的10个单词"]
            else:
                return ["背15个单词", "复习前一天的15个单词", "做5道单词选择题"]
        elif "阅读" in task_goal:
            if fragment_time <= 5:
                return ["阅读一段短文", "记录2个生词"]
            elif fragment_time <= 10:
                return ["阅读一篇短文", "记录5个生词", "回答2个理解问题"]
            else:
                return ["阅读一篇文章", "记录8个生词", "回答5个理解问题", "总结文章大意"]
        else:
            # 通用任务拆解
            if fragment_time <= 5:
                return [f"完成{task_goal}的第一步", f"准备{task_goal}的下一步"]
            elif fragment_time <= 10:
                return [f"完成{task_goal}的前两步", f"回顾{task_goal}的要点", f"准备{task_goal}的下一步"]
            else:
                return [f"完成{task_goal}的前三步", f"回顾{task_goal}的要点", f"整理{task_goal}的笔记", f"准备{task_goal}的下一步"]

class ResourceRecommendView(APIView):
    """自动推荐学习资源"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        task_name = request.data.get('task_name')
        if not task_name:
            return error_response(message="缺少任务名称", code=400)
        
        # 模拟资源推荐
        recommended_resources = self._recommend_resources(task_name)
        
        # 保存推荐结果
        resources = []
        for resource in recommended_resources:
            lr = LearningResource.objects.create(
                user=request.user,
                task_name=task_name,
                resource_type=resource['type'],
                title=resource['title'],
                url=resource['url'],
                description=resource['description']
            )
            resources.append({
                'resource_id': lr.id,
                'type': lr.resource_type,
                'title': lr.title,
                'url': lr.url,
                'description': lr.description
            })
        
        return success_response(
            data={"resources": resources},
            message="资源推荐成功",
            code=201
        )
    
    def _recommend_resources(self, current_task):
        """根据当前任务推荐资源"""
        # 这里可以实现更复杂的推荐算法，例如基于用户历史、相似度等
        # 这里使用简单的关键词匹配作为示例
        resources = []
        
        if "数学" in current_task:
            resources = [
                {
                    "title": "5分钟理解微积分基础概念",
                    "duration": "5分钟",
                    "url": "https://example.com/math/calculus-basics"
                },
                {
                    "title": "10分钟掌握函数图像变换",
                    "duration": "10分钟",
                    "url": "https://example.com/math/function-transformation"
                },
                {
                    "title": "3分钟记忆三角函数公式",
                    "duration": "3分钟",
                    "url": "https://example.com/math/trigonometry-formulas"
                }
            ]
        elif "英语" in current_task or "四级" in current_task:
            resources = [
                {
                    "title": "5分钟记忆20个高频词汇",
                    "duration": "5分钟",
                    "url": "https://example.com/english/vocabulary"
                },
                {
                    "title": "8分钟听力技巧训练",
                    "duration": "8分钟",
                    "url": "https://example.com/english/listening-skills"
                },
                {
                    "title": "4分钟掌握一个语法点",
                    "duration": "4分钟",
                    "url": "https://example.com/english/grammar-tips"
                }
            ]
        else:
            # 通用资源
            resources = [
                {
                    "title": "5分钟高效学习方法",
                    "duration": "5分钟",
                    "url": "https://example.com/study/effective-methods"
                },
                {
                    "title": "10分钟专注力训练",
                    "duration": "10分钟",
                    "url": "https://example.com/study/focus-training"
                },
                {
                    "title": "3分钟记忆技巧",
                    "duration": "3分钟",
                    "url": "https://example.com/study/memory-techniques"
                }
            ]
        
        return resources

class EmotionAnalyzeView(APIView):
    """学习情绪分析与调节建议"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EmotionRecordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            emotion_record = serializer.save()
            return success_response(
                data={
                    "emotion_detected": emotion_record.emotion,
                    "adjustment_suggestions": emotion_record.adjustment_suggestion
                },
                message="情绪分析完成",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

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

class AutoExecuteTaskView(APIView):
    """设置自动执行任务"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        task_plan = request.data.get('task_plan')
        auto_execute_switch = request.data.get('auto_execute_switch')
        
        if task_plan is None or auto_execute_switch is None:
            return error_response(message="缺少必要参数", code=400)
        
        serializer = AutoTaskSerializer(data={
            'task_plan': task_plan,
            'auto_execute_switch': auto_execute_switch
        }, context={'request': request})
        
        if serializer.is_valid():
            auto_task = serializer.save()
            return success_response(
                data={"message": "自动任务已设置"},
                message="设置成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

class AutoExecuteTaskCancelView(APIView):
    """取消自动执行任务"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        task = get_object_or_404(AutoTask, id=task_id, user=request.user)
        task.is_active = False
        task.save()
        
        return success_response(
            data={
                "task_id": task_id,
                "auto_execute_switch": task.is_active
            },
            message="任务已取消"
        )

class PlanStartView(APIView):
    """启动学习计划"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id, user=request.user)
        
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
            plan.save()
            
            return success_response(
                data={
                    "plan_id": plan_id,
                    "status": plan.status,
                    "start_time": start_time.isoformat()
                },
                message="计划启动成功"
            )
        return error_response(message=serializer.errors, code=400)

# 任务管理视图
class TaskListCreateView(APIView):
    """创建和获取任务列表"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """创建任务计划（含存钱计划）"""
        serializer = PlanCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            plan = serializer.save()
            return success_response(
                data={"task_id": str(plan.id)},
                message="任务创建成功",
                code=201
            )
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
            # 长期计划（超过一周的计划）
            today = query_date
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            plans = Plan.objects.filter(
                user=request.user, 
                scheduled_date__gt=end_of_week
            )
        else:
            return error_response(message="不支持的时间粒度", code=400)
        
        serializer = PlanSerializer(plans, many=True)
        return success_response(data={"tasks": serializer.data})

class TaskDetailView(APIView):
    """获取和更新任务详情"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        """获取任务详情"""
        plan = get_object_or_404(Plan, id=task_id, user=request.user)
        serializer = PlanSerializer(plan)
        return success_response(data=serializer.data)
    
    def put(self, request, task_id):
        """更新任务"""
        plan = get_object_or_404(Plan, id=task_id, user=request.user)
        serializer = PlanUpdateSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            plan = serializer.save()
            return success_response(
                data={"task_id": str(task_id)},
                message="任务更新成功"
            )
        return error_response(message=serializer.errors, code=400)

class TaskStartView(APIView):
    """开始任务计时"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        """启动任务计时"""
        plan = get_object_or_404(Plan, id=task_id, user=request.user)
        
        # 检查任务状态
        if plan.status == 'active':
            return error_response(message="任务已经在进行中", code=409)
        elif plan.status == 'completed':
            return error_response(message="任务已完成", code=409)
        
        serializer = PlanStartSerializer(data=request.data)
        if serializer.is_valid():
            # 更新任务状态
            plan.status = 'active'
            
            # 如果提供了开始时间，则使用提供的时间
            start_time = serializer.validated_data.get('start_time')
            if start_time:
                plan.start_time = start_time
            else:
                plan.start_time = timezone.now()
                
            plan.save()
            
            return success_response(
                data={
                    "task_id": str(task_id),
                    "status": plan.status,
                    "start_time": plan.start_time.isoformat()
                },
                message="任务已启动"
            )
        return error_response(message=serializer.errors, code=400)

class TaskPauseView(APIView):
    """暂停或重启任务"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        """暂停或重启指定任务的计时"""
        plan = get_object_or_404(Plan, id=task_id, user=request.user)
        serializer = PlanPauseResumeSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            
            if action == 'pause':
                # 如果任务正在进行中，计算已完成的专注时间
                if plan.status == 'active' and plan.start_time:
                    # 计算从开始到现在的分钟数
                    elapsed_time = (timezone.now() - plan.start_time).total_seconds() / 60
                    plan.completed_focus_time += int(elapsed_time)
                    
                    # 如果设置了存钱计划，计算解锁金额
                    if plan.savings_amount:
                        # 按比例计算解锁金额
                        completion_ratio = min(plan.completed_focus_time / plan.focus_time, 1.0)
                        plan.unlocked_savings = plan.savings_amount * completion_ratio
                
                plan.status = 'paused'
                message = "任务已暂停"
            
            elif action == 'resume':
                plan.status = 'active'
                plan.start_time = timezone.now()
                message = "任务已重启"
            
            plan.save()
            
            return success_response(
                data={
                    "task_id": task_id,
                    "status": plan.status
                },
                message=message
            )
        return error_response(message=serializer.errors, code=400)

# AI 计划视图
class AIGeneratePlanView(APIView):
    """AI 生成学习计划"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """根据目标和时间范围生成结构化计划"""
        serializer = AIGeneratedPlanSerializer(data=request.data)
        if serializer.is_valid():
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
            
            return success_response(
                data={"generated_plan": generated_plan},
                message="计划生成成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

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

# 任务处理视图
class FragmentTaskView(APIView):
    """任务碎片化"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """将指定任务拆解为微任务"""
        serializer = FragmentTaskSerializer(data=request.data)
        if serializer.is_valid():
            task_id = serializer.validated_data['task_id']
            fragment_time = serializer.validated_data['fragment_time']
            
            # 获取原任务
            original_task = get_object_or_404(Plan, id=task_id, user=request.user)
            
            # 计算需要拆分的碎片数量
            total_fragments = max(1, int(original_task.focus_time / fragment_time))
            
            # 创建碎片任务
            fragment_tasks = []
            for i in range(total_fragments):
                fragment_name = f"{original_task.task_name}（碎片{i+1}）"
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
        return error_response(message=serializer.errors, code=400)

# 资源管理视图
class ResourceRecommendView(APIView):
    """自动推荐学习资源"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """根据当前任务推荐适合碎片化学习的短时资源"""
        current_task = request.query_params.get('current_task')
        if not current_task:
            return error_response(message="缺少参数：current_task", code=400)
        
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
            resource = LearningResource.objects.get(id=resource_id)
        except LearningResource.DoesNotExist:
            return error_response(message="资源不存在", code=404)
        
        # 添加到用户收藏
        resource.favorited_by.add(request.user)
        
        return success_response(
            data={
                "resource_id": str(resource_id),
                "favorited": True
            },
            message="收藏成功"
        )

# 情绪分析视图
class EmotionAnalyzeView(APIView):
    """学习情绪分析与调节建议"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """通过用户反馈或传感器数据分析情绪，推荐调节任务"""
        serializer = EmotionRecordSerializer(data=request.data)
        if serializer.is_valid():
            user_feedback = serializer.validated_data['user_feedback']
            sensor_data = serializer.validated_data.get('sensor_data', '')
            
            # 创建情绪记录
            emotion_record = EmotionRecord.objects.create(
                user=request.user,
                feedback=user_feedback,
                sensor_data=sensor_data
            )
            
            # 简单情绪分析逻辑
            emotion_type = "未知"
            if any(word in user_feedback.lower() for word in ["疲倦", "累", "困", "乏力"]):
                emotion_type = "疲倦"
                suggestions = [
                    "建议听5分钟冥想音频",
                    "尝试站起来活动一下身体",
                    "喝一杯水，补充水分"
                ]
            elif any(word in user_feedback.lower() for word in ["焦虑", "紧张", "压力", "担心"]):
                emotion_type = "焦虑"
                suggestions = [
                    "进行深呼吸练习3分钟",
                    "写下你担心的事情，然后制定应对计划",
                    "尝试5分钟的正念冥想"
                ]
            elif any(word in user_feedback.lower() for word in ["分心", "注意力", "集中", "专注"]):
                emotion_type = "注意力分散"
                suggestions = [
                    "使用番茄工作法，25分钟专注后休息5分钟",
                    "清理桌面，减少视觉干扰",
                    "关闭手机通知，进入专注模式"
                ]
            else:
                suggestions = [
                    "保持当前良好状态",
                    "每完成一个任务给自己一个小奖励",
                    "定期回顾学习成果，增强成就感"
                ]
            
            return success_response(
                data={
                    "emotion_detected": emotion_type,
                    "adjustment_suggestions": suggestions[0]
                },
                message="情绪分析完成",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

class EmotionHistoryView(APIView):
    """获取情绪历史记录"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """查看历史情绪记录"""
        # 获取用户的情绪记录
        emotion_records = EmotionRecord.objects.filter(user=request.user).order_by('-created_at')[:10]
        
        # 构建历史记录
        history = []
        for record in emotion_records:
            # 简单情绪分析逻辑
            emotion_type = "未知"
            if any(word in record.feedback.lower() for word in ["疲倦", "累", "困", "乏力"]):
                emotion_type = "疲倦"
                suggestion = "建议听5分钟冥想音频"
            elif any(word in record.feedback.lower() for word in ["焦虑", "紧张", "压力", "担心"]):
                emotion_type = "焦虑"
                suggestion = "进行深呼吸练习3分钟"
            elif any(word in record.feedback.lower() for word in ["分心", "注意力", "集中", "专注"]):
                emotion_type = "注意力分散"
                suggestion = "使用番茄工作法，25分钟专注后休息5分钟"
            else:
                suggestion = "保持当前良好状态"
            
            history.append({
                "timestamp": record.created_at.isoformat(),
                "emotion_detected": emotion_type,
                "adjustment_suggestions": suggestion
            })
        
        return success_response(
            data={"history": history},
            message="获取情绪历史成功"
        )

# 语音助手视图
class VoiceAssistantView(APIView):
    """语音助手控制任务"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """通过语音创建计划或开始计时"""
        serializer = VoiceCommandSerializer(data=request.data)
        if serializer.is_valid():
            voice_command = serializer.validated_data['voice_command']
            
            # 解析命令并执行相应操作
            execution_result = "命令已接收"
            
            if "开始" in voice_command or "启动" in voice_command:
                # 解析任务名称和时间
                parts = voice_command.replace("开始", "").replace("启动", "").strip().split(" ")
                if len(parts) >= 2:
                    try:
                        time_part = parts[0]
                        focus_time = int(''.join(filter(str.isdigit, time_part)))
                        task_name = " ".join(parts[1:])
                        
                        # 创建并启动任务
                        plan = Plan.objects.create(
                            user=request.user,
                            task_name=task_name,
                            focus_time=focus_time,
                            rest_time=5,  # 默认休息时间
                            status='active',
                            start_time=timezone.now()
                        )
                        execution_result = f"已启动{focus_time}分钟的{task_name}任务"
                    except Exception as e:
                        execution_result = f"创建任务失败：{str(e)}"
                else:
                    execution_result = "命令格式不正确，请说明时间和任务名称"
            
            elif "暂停" in voice_command:
                # 暂停当前进行中的任务
                active_task = Plan.objects.filter(user=request.user, status='active').first()
                if active_task:
                    active_task.status = 'paused'
                    active_task.save()
                    execution_result = f"已暂停任务：{active_task.task_name}"
                else:
                    execution_result = "没有正在进行的任务"
            
            elif "继续" in voice_command or "恢复" in voice_command:
                # 恢复暂停的任务
                paused_task = Plan.objects.filter(user=request.user, status='paused').first()
                if paused_task:
                    paused_task.status = 'active'
                    paused_task.start_time = timezone.now()
                    paused_task.save()
                    execution_result = f"已恢复任务：{paused_task.task_name}"
                else:
                    execution_result = "没有暂停的任务"
            
            elif "创建" in voice_command or "新建" in voice_command:
                # 解析创建任务命令
                parts = voice_command.replace("创建", "").replace("新建", "").replace("任务", "").split("，")
                if len(parts) >= 2:
                    try:
                        task_name = parts[0].strip()
                        time_part = parts[1].strip()
                        focus_time = int(''.join(filter(str.isdigit, time_part)))
                        
                        plan = Plan.objects.create(
                            user=request.user,
                            task_name=task_name,
                            focus_time=focus_time,
                            rest_time=5  # 默认休息时间
                        )
                        execution_result = f"已创建任务：{task_name}，专注时间{focus_time}分钟"
                    except Exception as e:
                        execution_result = f"创建任务时出错：{str(e)}"
                else:
                    execution_result = "命令格式不正确，请说明任务名称和时间"
            
            return success_response(
                data={"execution_result": execution_result},
                message="指令执行成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

# 自动化任务视图
class AutoTaskView(APIView):
    """设置自动执行任务"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """开启自动模式，到指定时间自动开始任务"""
        serializer = AutoTaskSerializer(data=request.data)
        if serializer.is_valid():
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
                data={"message": "自动任务已设置"},
                message="设置成功",
                code=201
            )
        return error_response(message=serializer.errors, code=400)

class AutoTaskCancelView(APIView):
    """取消自动执行任务"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, task_id):
        """取消指定自动执行任务"""
        auto_task = get_object_or_404(AutoTask, id=task_id, user=request.user)
        auto_task.is_active = False
        auto_task.save()
        
        return success_response(
            data={
                "task_id": str(task_id),
                "auto_execute_switch": auto_task.is_active
            },
            message="任务已取消"
        ) 