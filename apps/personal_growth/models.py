# 个人提升模块模型 
from django.db import models
from django.conf import settings

class Plan(models.Model):
    """
    学习计划模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plans', verbose_name="用户")
    task_name = models.CharField(max_length=100, verbose_name="任务名称")
    focus_time = models.IntegerField(verbose_name="专注时长(分钟)")
    rest_time = models.IntegerField(verbose_name="休息时长(分钟)")
    savings_amount = models.FloatField(null=True, blank=True, verbose_name="存钱金额")
    completed_focus_time = models.IntegerField(default=0, verbose_name="已完成专注时长(分钟)")
    unlocked_savings = models.FloatField(default=0.0, verbose_name="已解锁存钱金额")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "学习计划"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "自动执行任务"
        verbose_name_plural = verbose_name
        ordering = ['execution_time']
    
    def __str__(self):
        return f"{self.user.username}的自动任务: {self.task_description}" 