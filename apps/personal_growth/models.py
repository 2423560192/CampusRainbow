# 个人提升模块模型 
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Plan(models.Model):
    """
    学习计划模型（番茄任务）
    """
    STATUS_CHOICES = (
        ('pending', '待开始'),
        ('active', '进行中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plans', verbose_name="用户")
    task_name = models.CharField(max_length=100, verbose_name="任务名称")
    focus_time = models.PositiveIntegerField(verbose_name="专注时长(分钟)")
    rest_time = models.PositiveIntegerField(verbose_name="休息时长(分钟)")
    savings_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="存钱金额")
    completed_focus_time = models.PositiveIntegerField(default=0, verbose_name="已完成专注时长(分钟)")
    unlocked_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="已解锁金额")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    scheduled_date = models.DateField(default=timezone.now, verbose_name="计划执行日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    
    class Meta:
        verbose_name = "学习计划"
        verbose_name_plural = verbose_name
        ordering = ['scheduled_date', '-created_at']
    
    def __str__(self):
        return f"{self.user.username}的{self.task_name}计划"

class AIGeneratedPlan(models.Model):
    """
    AI生成的学习计划模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_plans', verbose_name="用户")
    goal_description = models.CharField(max_length=500, verbose_name="目标描述")
    time_range = models.CharField(max_length=100, verbose_name="时间范围")
    current_level = models.CharField(max_length=200, blank=True, null=True, verbose_name="当前水平")
    plan_content = models.JSONField(verbose_name="计划内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "AI生成学习计划"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的{self.goal_description}计划"

class FragmentTask(models.Model):
    """
    碎片化任务模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fragment_tasks', verbose_name="用户")
    parent_task = models.CharField(max_length=200, verbose_name="父任务")
    fragment_time = models.IntegerField(verbose_name="碎片时间(分钟)")
    micro_tasks = models.JSONField(verbose_name="微任务列表")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "碎片化任务"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的{self.parent_task}碎片任务"

class LearningResource(models.Model):
    """
    学习资源模型
    """
    title = models.CharField(max_length=200, verbose_name="资源标题")
    duration = models.CharField(max_length=50, verbose_name="资源时长")
    url = models.URLField(verbose_name="资源链接")
    category = models.CharField(max_length=100, verbose_name="资源分类")
    tags = models.JSONField(default=list, verbose_name="标签")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "学习资源"
        verbose_name_plural = verbose_name
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.duration})"

class UserResourceFavorite(models.Model):
    """
    用户资源收藏模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resource_favorites', verbose_name="用户")
    resource = models.ForeignKey(LearningResource, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="资源")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "用户资源收藏"
        verbose_name_plural = verbose_name
        unique_together = ['user', 'resource']
    
    def __str__(self):
        return f"{self.user.username}收藏的{self.resource.title}"

class EmotionRecord(models.Model):
    """
    情绪记录模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='emotion_records', verbose_name="用户")
    emotion = models.CharField(max_length=100, verbose_name="情绪")
    sensor_data = models.JSONField(blank=True, null=True, verbose_name="传感器数据")
    adjustment_suggestion = models.TextField(verbose_name="调节建议")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "情绪记录"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的情绪记录: {self.emotion}"

class VoiceCommand(models.Model):
    """
    语音指令记录模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_commands', verbose_name="用户")
    command = models.CharField(max_length=500, verbose_name="指令内容")
    execution_result = models.TextField(verbose_name="执行结果")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "语音指令"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的语音指令: {self.command}"

class AutoTask(models.Model):
    """
    自动执行任务模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auto_tasks', verbose_name="用户")
    task_description = models.CharField(max_length=200, verbose_name="任务描述")
    execution_time = models.CharField(max_length=100, verbose_name="执行时间")
    repeat_pattern = models.CharField(max_length=100, blank=True, null=True, verbose_name="重复模式")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    reminder_minutes = models.PositiveIntegerField(default=5, verbose_name="提前提醒时间(分钟)")
    scheduled_date = models.DateField(default=timezone.now, verbose_name="计划执行日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "自动执行任务"
        verbose_name_plural = verbose_name
        ordering = ['execution_time']
    
    def __str__(self):
        return f"{self.user.username}的自动任务: {self.task_description}"

class PomodoroSession(models.Model):
    """
    番茄钟会话模型
    """
    STATUS_CHOICES = (
        ('created', '已创建'),
        ('in_progress', '进行中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pomodoro_sessions', verbose_name="用户")
    task = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='pomodoro_sessions', verbose_name="关联任务")
    title = models.CharField(max_length=100, verbose_name="会话标题")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="状态")
    focus_minutes = models.IntegerField(default=25, verbose_name="专注时长(分钟)")
    break_minutes = models.IntegerField(default=5, verbose_name="休息时长(分钟)")
    long_break_minutes = models.IntegerField(default=15, verbose_name="长休息时长(分钟)")
    long_break_interval = models.IntegerField(default=4, verbose_name="长休息间隔")
    completed_pomodoros = models.IntegerField(default=0, verbose_name="已完成番茄钟数量")
    planned_pomodoros = models.IntegerField(default=0, verbose_name="计划番茄钟数量")
    total_focus_time = models.IntegerField(default=0, verbose_name="总专注时长(分钟)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    
    class Meta:
        verbose_name = "番茄钟会话"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的{self.title}会话"

class PomodoroRecord(models.Model):
    """
    番茄钟记录模型
    """
    session = models.ForeignKey(PomodoroSession, on_delete=models.CASCADE, related_name='pomodoro_records', verbose_name="会话")
    pomodoro_number = models.IntegerField(verbose_name="番茄钟序号")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    actual_duration = models.IntegerField(default=0, verbose_name="实际持续时间(分钟)")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    notes = models.TextField(blank=True, null=True, verbose_name="笔记")
    
    class Meta:
        verbose_name = "番茄钟记录"
        verbose_name_plural = verbose_name
        ordering = ['session', 'pomodoro_number']
        unique_together = ['session', 'pomodoro_number']
    
    def __str__(self):
        return f"{self.session.title}的第{self.pomodoro_number}个番茄钟" 