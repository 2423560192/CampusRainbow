# 个人提升模块序列化器 
from rest_framework import serializers
from .models import Plan, AIGeneratedPlan, FragmentTask, LearningResource, EmotionRecord, VoiceCommand, AutoTask


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
    task_plan = serializers.JSONField(write_only=True)
    auto_execute_switch = serializers.BooleanField(write_only=True)

    class Meta:
        model = AutoTask
        fields = (
        'task_description', 'execution_time', 'repeat_pattern', 'is_active', 'task_plan', 'auto_execute_switch')
        read_only_fields = ('task_description', 'execution_time', 'repeat_pattern', 'is_active')

    def create(self, validated_data):
        user = self.context['request'].user
        task_plan = validated_data.pop('task_plan')
        auto_execute_switch = validated_data.pop('auto_execute_switch')

        task_description = task_plan.get('task', '')
        execution_time = task_plan.get('time', '')

        return AutoTask.objects.create(
            user=user,
            task_description=task_description,
            execution_time=execution_time,
            is_active=auto_execute_switch
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
