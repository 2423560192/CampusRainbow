from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 用户模块
    path('user/', include('apps.user.urls')),
    # 个人提升模块
    path('', include('apps.personal_growth.urls')),
    # 校园规划模块
    path('', include('apps.campus_planning.urls')),
    # 虚拟自习室模块
    path('', include('apps.virtual_study_room.urls')),
    # 生活助手模块
    path('', include('apps.life_assistant.urls')),
] 