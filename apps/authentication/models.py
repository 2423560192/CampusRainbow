from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    自定义用户模型
    """
    student_id = models.CharField(max_length=20, blank=True, null=True, verbose_name="学号")
    university = models.CharField(max_length=100, blank=True, null=True, verbose_name="学校")
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name="专业")
    grade = models.CharField(max_length=20, blank=True, null=True, verbose_name="年级")
    avatar = models.URLField(blank=True, null=True, verbose_name="头像")
    
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        
    def __str__(self):
        return self.username 