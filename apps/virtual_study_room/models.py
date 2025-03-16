# 虚拟自习室模块模型 
from django.db import models
from django.conf import settings

class StudyRoom(models.Model):
    """
    自习室模型
    """
    ROOM_TYPE_CHOICES = (
        ('fragment', '碎片化自习室'),
        ('standard', '标准自习室'),
        ('ai_hosted', 'AI主持自习室'),
    )
    
    name = models.CharField(max_length=100, verbose_name="自习室名称")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, verbose_name="自习室类型")
    topic = models.CharField(max_length=100, verbose_name="学习主题")
    max_users = models.IntegerField(default=10, verbose_name="最大用户数")
    current_users = models.IntegerField(default=0, verbose_name="当前用户数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "自习室"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

class StudyRoomMember(models.Model):
    """
    自习室成员模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_room_memberships', verbose_name="用户")
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='members', verbose_name="自习室")
    join_time = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    leave_time = models.DateTimeField(blank=True, null=True, verbose_name="离开时间")
    study_goal = models.CharField(max_length=200, blank=True, null=True, verbose_name="学习目标")
    
    class Meta:
        verbose_name = "自习室成员"
        verbose_name_plural = verbose_name
        ordering = ['-join_time']
    
    def __str__(self):
        return f"{self.user.username}在{self.room.name}自习室"

class StudyRecord(models.Model):
    """
    学习记录模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_records', verbose_name="用户")
    room = models.ForeignKey(StudyRoom, on_delete=models.SET_NULL, null=True, related_name='records', verbose_name="自习室")
    duration = models.IntegerField(verbose_name="学习时长(分钟)")
    content = models.TextField(verbose_name="学习内容")
    completion_rate = models.FloatField(verbose_name="完成率")
    blockchain_hash = models.CharField(max_length=200, blank=True, null=True, verbose_name="区块链哈希")
    verification_url = models.URLField(blank=True, null=True, verbose_name="验证链接")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "学习记录"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的学习记录({self.created_at.strftime('%Y-%m-%d')})"

class AIHostedStudySession(models.Model):
    """
    AI主持自习会话模型
    """
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='ai_sessions', verbose_name="自习室")
    room_goal = models.CharField(max_length=200, verbose_name="自习室目标")
    duration = models.IntegerField(verbose_name="计划时长(分钟)")
    suggestions = models.TextField(blank=True, null=True, verbose_name="AI建议")
    summary_report = models.TextField(blank=True, null=True, verbose_name="总结报告")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    
    class Meta:
        verbose_name = "AI主持自习会话"
        verbose_name_plural = verbose_name
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.room.name}的AI主持会话({self.start_time.strftime('%Y-%m-%d %H:%M')})" 