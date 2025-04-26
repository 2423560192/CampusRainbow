import os
from celery import Celery

# 设置默认Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoyuanyunbao.settings')

app = Celery('xiaoyuanyunbao')

# 使用字符串，这样worker不用序列化配置对象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的app中加载任务模块
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 