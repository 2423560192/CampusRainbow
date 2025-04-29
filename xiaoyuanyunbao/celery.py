import os
from celery import Celery
from kombu import Exchange, Queue
import logging

# 设置默认Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xiaoyuanyunbao.settings')

app = Celery('xiaoyuanyunbao')

# 使用字符串，这样worker不用序列化配置对象
app.config_from_object('django.conf:settings', namespace='CELERY')

# 定义队列
default_exchange = Exchange('default', type='direct')
user_exchange = Exchange('users', type='direct')
life_assistant_exchange = Exchange('life_assistant', type='direct')
study_room_exchange = Exchange('study_room', type='direct')
personal_growth_exchange = Exchange('personal_growth', type='direct')
campus_planning_exchange = Exchange('campus_planning', type='direct')

# 配置队列
app.conf.task_queues = (
    Queue('default', default_exchange, routing_key='default'),
    Queue('users', user_exchange, routing_key='users'),
    Queue('life_assistant', life_assistant_exchange, routing_key='life_assistant'),
    Queue('study_room', study_room_exchange, routing_key='study_room'),
    Queue('personal_growth', personal_growth_exchange, routing_key='personal_growth'),
    Queue('campus_planning', campus_planning_exchange, routing_key='campus_planning'),
)

# 设置默认队列
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# 设置错误处理
app.conf.task_annotations = {
    '*': {
        'rate_limit': '10/s',  # 全局速率限制
        'max_retries': 3,      # 最大重试次数
    },
}

# 配置Redis连接池 - 提高并发性能
app.conf.broker_pool_limit = 20  # Redis连接池大小
app.conf.broker_connection_max_retries = 3  # 连接重试次数

# 设置日志
logger = logging.getLogger('celery')
logger.setLevel(logging.INFO)

# 从所有已注册的app中加载任务模块
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 