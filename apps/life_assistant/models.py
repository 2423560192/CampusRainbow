# 生活助手模块模型 
from django.db import models
from django.conf import settings

class WeatherRecord(models.Model):
    """
    天气记录模型
    """
    location = models.CharField(max_length=100, verbose_name="位置")
    weather_info = models.CharField(max_length=200, verbose_name="天气信息")
    temperature = models.CharField(max_length=50, verbose_name="温度")
    health_tips = models.TextField(verbose_name="养生建议")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "天气记录"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.location}的天气记录({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class ExpressPackage(models.Model):
    """
    快递包裹模型
    """
    STATUS_CHOICES = (
        ('pending', '待发货'),
        ('shipped', '运输中'),
        ('arrived', '已到达'),
        ('delivered', '已签收'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='express_packages', verbose_name="用户")
    tracking_number = models.CharField(max_length=100, verbose_name="快递单号")
    carrier = models.CharField(max_length=100, blank=True, null=True, verbose_name="快递公司")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="快递状态")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="当前位置")
    pickup_suggestion = models.CharField(max_length=200, blank=True, null=True, verbose_name="取件建议")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "快递包裹"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的快递: {self.tracking_number}"

class DormitoryTask(models.Model):
    """
    宿舍待办事项模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dormitory_tasks', verbose_name="用户")
    description = models.CharField(max_length=500, verbose_name="待办描述")
    execution_preference = models.CharField(max_length=100, blank=True, null=True, verbose_name="执行时间偏好")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="完成时间")
    
    class Meta:
        verbose_name = "宿舍待办事项"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的待办: {self.description}"

class DormitoryTaskCollaboration(models.Model):
    """
    宿舍待办协作模型
    """
    task = models.ForeignKey(DormitoryTask, on_delete=models.CASCADE, related_name='collaborators', verbose_name="待办事项")
    collaborator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collaborative_tasks', verbose_name="协作者")
    is_accepted = models.BooleanField(default=False, verbose_name="是否接受")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "宿舍待办协作"
        verbose_name_plural = verbose_name
        unique_together = ['task', 'collaborator']
    
    def __str__(self):
        return f"{self.collaborator.username}协作{self.task.description}" 