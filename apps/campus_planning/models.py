# 校园规划模块模型 
from django.db import models
from django.conf import settings

class Schedule(models.Model):
    """
    日程规划模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules', verbose_name="用户")
    date = models.DateField(verbose_name="日期")
    content = models.JSONField(verbose_name="日程内容")
    preferences = models.JSONField(blank=True, null=True, verbose_name="时间偏好")
    avoid_times = models.JSONField(blank=True, null=True, verbose_name="避开时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "日程规划"
        verbose_name_plural = verbose_name
        ordering = ['-date']
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username}的日程({self.date})"

class CourseSchedule(models.Model):
    """
    课表模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_schedules', verbose_name="用户")
    course_name = models.CharField(max_length=100, verbose_name="课程名称")
    day_of_week = models.IntegerField(verbose_name="星期几(1-7)")
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="上课地点")
    semester = models.CharField(max_length=100, verbose_name="学期")
    
    class Meta:
        verbose_name = "课表"
        verbose_name_plural = verbose_name
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.user.username}的{self.course_name}课程"

class PartnerRequest(models.Model):
    """
    搭子请求模型
    """
    STATUS_CHOICES = (
        ('pending', '待匹配'),
        ('matched', '已匹配'),
        ('cancelled', '已取消'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='partner_requests', verbose_name="用户")
    activity_type = models.CharField(max_length=100, verbose_name="活动类型")
    preferred_time = models.CharField(max_length=100, blank=True, null=True, verbose_name="偏好时间")
    interests = models.JSONField(default=list, verbose_name="兴趣爱好")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="位置")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="状态")
    matched_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='matched_requests',
        verbose_name="匹配用户"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "搭子请求"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的{self.activity_type}搭子请求" 