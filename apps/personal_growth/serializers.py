# 个人提升模块序列化器 
from rest_framework import serializers
from .models import Plan, AIGeneratedPlan, FragmentTask, LearningResource, EmotionRecord, VoiceCommand, AutoTask, PomodoroRecord, PomodoroSession
from django.utils.dateparse import parse_date
from django.utils import timezone


class PlanSerializer(serializers.ModelSerializer):
    """学习计划序列化器"""
    task_id = serializers.CharField(source='id', read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ('task_id', 'task_name', 'focus_time', 'rest_time', 'savings_amount',
                  'completed_focus_time', 'unlocked_savings', 'status', 'progress', 
                  'scheduled_date', 'created_at')
        read_only_fields = ('task_id', 'completed_focus_time', 'unlocked_savings', 'created_at')
    
    def get_progress(self, obj):
        if obj.focus_time > 0:
            completion_percentage = (obj.completed_focus_time / obj.focus_time) * 100
            progress_message = f"已完成{obj.completed_focus_time}分钟，完成率{completion_percentage:.1f}%"
            
            if obj.savings_amount:
                progress_message += f"，解锁{obj.unlocked_savings}元"
            
            return progress_message
        return "尚未开始"


class PlanCreateSerializer(serializers.ModelSerializer):
    """创建学习计划序列化器"""
    scheduled_date = serializers.DateField(required=False)
    
    class Meta:
        model = Plan
        fields = ('task_name', 'focus_time', 'rest_time', 'savings_amount', 'scheduled_date')
        extra_kwargs = {
            'savings_amount': {'required': False}
        }
    
    def validate_focus_time(self, value):
        if value < 1 or value > 120:
            raise serializers.ValidationError("专注时长必须在1-120分钟之间")
        return value
    
    def validate_rest_time(self, value):
        if value < 1 or value > 60:
            raise serializers.ValidationError("休息时长必须在1-60分钟之间")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Plan.objects.create(user=user, **validated_data)


class TaskCreateSerializer(serializers.Serializer):
    """符合API文档的任务创建序列化器"""
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=False, allow_null=True)
    priority = serializers.ChoiceField(
        choices=['low', 'medium', 'high'], 
        default='medium',
        required=False
    )
    due_date = serializers.CharField(required=False, allow_null=True)
    estimated_time = serializers.IntegerField(required=False, allow_null=True)
    subtasks = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_null=True
    )
    
    def validate_estimated_time(self, value):
        if value is not None and (value < 1 or value > 480):
            raise serializers.ValidationError("预计完成时间应在1-480分钟之间")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        title = validated_data.get('title')
        description = validated_data.get('description', '')
        estimated_time = validated_data.get('estimated_time', 25)  # 默认25分钟
        
        # 创建Plan模型实例
        plan = Plan.objects.create(
            user=user,
            task_name=title,
            focus_time=estimated_time,
            rest_time=5,  # 默认休息时间5分钟
            status='pending'
        )
        
        # 如果有截止日期，设置计划执行日期
        if validated_data.get('due_date'):
            due_date_str = validated_data.get('due_date')
            # 处理字符串格式的日期
            if isinstance(due_date_str, str):
                # 如果是ISO格式的datetime字符串
                if 'T' in due_date_str:
                    due_date_str = due_date_str.split('T')[0]
                # 现在应该是YYYY-MM-DD格式
                due_date = parse_date(due_date_str)
                if due_date:
                    plan.scheduled_date = due_date
                    plan.save()
            
        return plan


class TaskSerializer(serializers.ModelSerializer):
    """符合API文档的任务序列化器"""
    task_id = serializers.CharField(source='id', read_only=True)
    title = serializers.CharField(source='task_name')
    description = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()
    due_date = serializers.DateField(source='scheduled_date')
    estimated_time = serializers.IntegerField(source='focus_time')
    actual_time = serializers.IntegerField(source='completed_focus_time')
    subtasks = serializers.SerializerMethodField()
    
    class Meta:
        model = Plan
        fields = ('task_id', 'title', 'description', 'status', 'priority', 
                  'due_date', 'created_at', 'estimated_time', 'actual_time', 'subtasks')
    
    def get_description(self, obj):
        # Plan模型没有description字段，返回空字符串
        return ""
    
    def get_priority(self, obj):
        # 根据focus_time设置优先级
        if obj.focus_time > 60:
            return "high"
        elif obj.focus_time > 30:
            return "medium"
        return "low"
    
    def get_subtasks(self, obj):
        # 返回空列表，因为当前模型没有子任务
        return []


class PlanUpdateSerializer(serializers.ModelSerializer):
    """更新学习计划序列化器"""
    
    class Meta:
        model = Plan
        fields = ('task_name', 'focus_time', 'rest_time', 'savings_amount', 'scheduled_date')
        extra_kwargs = {
            'task_name': {'required': False},
            'focus_time': {'required': False},
            'rest_time': {'required': False},
            'savings_amount': {'required': False},
            'scheduled_date': {'required': False}
        }


class PlanPauseResumeSerializer(serializers.Serializer):
    """暂停或重启学习计划序列化器"""
    action = serializers.ChoiceField(choices=['pause', 'resume'], required=True)


class AIGeneratedPlanSerializer(serializers.ModelSerializer):
    """AI生成学习计划序列化器"""

    class Meta:
        model = AIGeneratedPlan
        fields = ('goal_description', 'time_range', 'current_level', 'plan_content')
        extra_kwargs = {
            'goal_description': {'required': True},
            'time_range': {'required': True},
            'current_level': {'required': False},
            'plan_content': {'required': False}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        return AIGeneratedPlan.objects.create(user=user, **validated_data)


class FragmentTaskSerializer(serializers.Serializer):
    """任务碎片化序列化器"""
    task_id = serializers.CharField(required=True)
    fragment_time = serializers.IntegerField(required=True, min_value=5, max_value=15)


class LearningResourceSerializer(serializers.ModelSerializer):
    """学习资源序列化器"""

    class Meta:
        model = LearningResource
        fields = ('title', 'duration', 'url', 'category', 'tags')


class EmotionRecordSerializer(serializers.ModelSerializer):
    """情绪记录序列化器"""

    class Meta:
        model = EmotionRecord
        fields = ('emotion', 'sensor_data', 'adjustment_suggestion')
        extra_kwargs = {
            'sensor_data': {'required': False},
            'adjustment_suggestion': {'read_only': True}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        # 这里可以添加情绪分析逻辑，生成调节建议
        adjustment_suggestion = self._generate_adjustment_suggestion(validated_data['emotion'])
        validated_data['adjustment_suggestion'] = adjustment_suggestion
        return EmotionRecord.objects.create(user=user, **validated_data)

    def _generate_adjustment_suggestion(self, emotion):
        """根据情绪生成调节建议"""
        suggestions = {
            '疲倦': '建议听5分钟冥想音频，或者做2分钟的伸展运动',
            '焦虑': '建议进行3分钟的深呼吸练习，或者喝一杯温水',
            '压力': '建议短暂休息，看看窗外风景，或者做一些简单的放松活动',
            '无聊': '建议切换到更有趣的学习内容，或者设定一个小目标增加动力',
            '困惑': '建议寻找更简单的学习资料，或者分解当前的学习内容'
        }
        return suggestions.get(emotion, '建议短暂休息，调整心态后再继续学习')


class EmotionAnalysisSerializer(serializers.Serializer):
    """情绪分析序列化器 - 与OpenAPI /emotions/analysis 端点兼容"""
    session_id = serializers.CharField(required=False, allow_null=True)
    text = serializers.CharField(required=True)
    image_data = serializers.CharField(required=False, allow_null=True)

    def create(self, validated_data):
        user = self.context['request'].user
        text = validated_data.get('text', '')
        
        # 从文本中提取情绪
        emotion = self._detect_emotion_from_text(text)
        
        # 生成调节建议
        adjustment_suggestion = self._generate_adjustment_suggestion(emotion)
        
        # 创建情绪记录
        return EmotionRecord.objects.create(
            user=user,
            emotion=emotion,
            sensor_data={'text': text, 'image_data': validated_data.get('image_data')},
            adjustment_suggestion=adjustment_suggestion
        )
    
    def _detect_emotion_from_text(self, text):
        """从文本中检测情绪"""
        if any(word in text for word in ["疲惫", "累", "困", "乏力", "没精神"]):
            return "疲倦"
        elif any(word in text for word in ["焦虑", "紧张", "压力", "担心", "害怕"]):
            return "焦虑"
        elif any(word in text for word in ["压力", "紧张", "负担", "重担"]):
            return "压力"
        elif any(word in text for word in ["无聊", "枯燥", "乏味", "没意思"]):
            return "无聊"
        elif any(word in text for word in ["困惑", "不懂", "迷茫", "不理解"]):
            return "困惑"
        else:
            return "中性"
    
    def _generate_adjustment_suggestion(self, emotion):
        """根据情绪生成调节建议"""
        suggestions = {
            '疲倦': '检测到你可能有些疲惫了，建议休息10分钟，出去走走或喝杯水，然后再继续学习',
            '焦虑': '检测到你可能有些焦虑，建议深呼吸5分钟，或者做一些简单的放松活动',
            '压力': '检测到你可能感到压力较大，建议短暂休息，听一段轻音乐，调整心态',
            '无聊': '检测到你可能觉得学习内容有些枯燥，建议换一种学习方式或设定小目标增加动力',
            '困惑': '检测到你可能对学习内容感到困惑，建议寻找更简单的学习材料或请教他人',
            '中性': '您的情绪状态良好，建议保持当前的学习节奏'
        }
        return suggestions.get(emotion, '建议短暂休息，调整心态后再继续学习')


class VoiceCommandSerializer(serializers.ModelSerializer):
    """语音指令序列化器"""

    class Meta:
        model = VoiceCommand
        fields = ('command', 'execution_result')
        extra_kwargs = {
            'execution_result': {'read_only': True}
        }

    def create(self, validated_data):
        user = self.context['request'].user
        # 这里可以添加语音指令解析逻辑，生成执行结果
        execution_result = self._process_voice_command(validated_data['command'])
        validated_data['execution_result'] = execution_result
        return VoiceCommand.objects.create(user=user, **validated_data)

    def _process_voice_command(self, command):
        """处理语音指令"""
        if '开始' in command and '分钟' in command:
            return '计时界面已启动'
        elif '创建计划' in command:
            return '已为您打开创建计划界面'
        elif '查看' in command and '计划' in command:
            return '已为您显示计划列表'
        else:
            return '无法识别的指令，请重试'


class AutoTaskSerializer(serializers.ModelSerializer):
    """自动执行任务序列化器"""
    task_plan = serializers.JSONField(required=True)
    auto_execute_switch = serializers.BooleanField(required=True)
    reminder_minutes = serializers.IntegerField(required=False, default=5)
    scheduled_date = serializers.DateField(required=False)

    class Meta:
        model = AutoTask
        fields = (
            'task_description', 'execution_time', 'repeat_pattern', 'is_active', 
            'task_plan', 'auto_execute_switch', 'reminder_minutes', 'scheduled_date'
        )
        read_only_fields = ('task_description', 'execution_time', 'repeat_pattern', 'is_active')

    def validate_task_plan(self, value):
        """验证task_plan格式"""
        if not isinstance(value, dict):
            try:
                # 尝试将字符串转换为字典
                if isinstance(value, str):
                    import json
                    value = json.loads(value)
            except Exception as e:
                raise serializers.ValidationError(f"task_plan必须是有效的JSON对象: {str(e)}")
        
        # 检查必要的键
        if 'task' not in value:
            raise serializers.ValidationError("task_plan必须包含'task'字段")
        if 'time' not in value:
            raise serializers.ValidationError("task_plan必须包含'time'字段")
            
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        task_plan = validated_data.pop('task_plan')
        auto_execute_switch = validated_data.pop('auto_execute_switch')
        reminder_minutes = validated_data.pop('reminder_minutes', 5)
        scheduled_date = validated_data.pop('scheduled_date', timezone.now().date())

        task_description = task_plan.get('task', '')
        execution_time = task_plan.get('time', '')

        return AutoTask.objects.create(
            user=user,
            task_description=task_description,
            execution_time=execution_time,
            is_active=auto_execute_switch,
            reminder_minutes=reminder_minutes,
            scheduled_date=scheduled_date
        )


class PlanStartSerializer(serializers.Serializer):
    """启动学习计划序列化器"""
    start_time = serializers.DateTimeField(required=False)


class AIAnalyzePlanSerializer(serializers.Serializer):
    """分析单独输入的计划序列化器"""
    plan_text = serializers.CharField(required=True)
    granularity = serializers.ChoiceField(
        choices=['day', 'week', 'long-term'], 
        default='day',
        required=False
    )


# 番茄钟会话序列化器
class PomodoroRecordSerializer(serializers.ModelSerializer):
    """番茄钟记录序列化器"""
    
    class Meta:
        model = PomodoroRecord
        fields = ['pomodoro_number', 'start_time', 'end_time', 'actual_duration', 'is_completed', 'notes']


class PomodoroSessionCreateSerializer(serializers.ModelSerializer):
    """创建番茄钟会话序列化器"""
    task_id = serializers.CharField(required=False, allow_null=True)
    
    class Meta:
        model = PomodoroSession
        fields = ['task_id', 'title', 'focus_minutes', 'break_minutes', 
                  'long_break_minutes', 'long_break_interval', 'planned_pomodoros']
    
    def validate(self, data):
        # 如果没有提供task_id，title必须提供
        if not data.get('task_id') and not data.get('title'):
            raise serializers.ValidationError("无关联任务时，会话标题必须提供")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        task_id = validated_data.pop('task_id', None)
        
        # 如果提供了task_id，尝试获取任务
        task = None
        if task_id:
            try:
                # 先尝试将task_id转为整数查询
                numeric_id = None
                try:
                    numeric_id = int(task_id)
                except (ValueError, TypeError):
                    pass
                
                if numeric_id is not None:
                    task = Plan.objects.get(id=numeric_id, user=user)
                else:
                    # 如果不是数字ID，默认选择第一个任务（用于演示）
                    # 实际应用中可能需要更复杂的逻辑
                    task = Plan.objects.filter(user=user).first()
                    if not task:
                        raise Plan.DoesNotExist
                
                # 如果没有提供title，使用任务名称作为标题
                if not validated_data.get('title'):
                    validated_data['title'] = task.task_name
            except Plan.DoesNotExist:
                raise serializers.ValidationError({"task_id": "指定的任务不存在"})
        
        # 创建番茄钟会话
        session = PomodoroSession.objects.create(
            user=user,
            task=task,
            **validated_data
        )
        return session


class PomodoroSessionSerializer(serializers.ModelSerializer):
    """番茄钟会话列表序列化器"""
    
    class Meta:
        model = PomodoroSession
        fields = ['session_id', 'title', 'status', 'completed_pomodoros', 'planned_pomodoros', 
                  'total_focus_time', 'created_at', 'completed_at']
    
    session_id = serializers.SerializerMethodField()
    
    def get_session_id(self, obj):
        return str(obj.id)


class PomodoroSessionDetailSerializer(serializers.ModelSerializer):
    """番茄钟会话详情序列化器"""
    pomodoro_records = PomodoroRecordSerializer(many=True, read_only=True)
    task_id = serializers.SerializerMethodField()
    session_id = serializers.SerializerMethodField()
    
    class Meta:
        model = PomodoroSession
        fields = ['session_id', 'title', 'task_id', 'status', 'focus_minutes', 'break_minutes', 
                  'long_break_minutes', 'long_break_interval', 'completed_pomodoros', 
                  'planned_pomodoros', 'total_focus_time', 'created_at', 'completed_at', 
                  'pomodoro_records']
    
    def get_task_id(self, obj):
        return str(obj.task.id) if obj.task else None
    
    def get_session_id(self, obj):
        return str(obj.id)


class PomodoroSessionUpdateSerializer(serializers.Serializer):
    """更新番茄钟会话状态序列化器"""
    action = serializers.ChoiceField(choices=['start', 'pause', 'resume', 'complete', 'cancel'])
    current_pomodoro = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
