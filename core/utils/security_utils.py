import logging
import ipaddress
from django.utils.timezone import now

# 获取安全日志记录器
security_logger = logging.getLogger('security')
auth_logger = logging.getLogger('user.auth')

def log_security_event(request, event_type, message, user=None, additional_data=None):
    """
    记录安全相关事件
    
    参数:
        request: Django请求对象
        event_type: 事件类型 (如 'login', 'logout', 'password_change', 'access_denied')
        message: 事件描述消息
        user: 用户对象 (可选)
        additional_data: 额外数据字典 (可选)
    """
    # 获取用户IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    # 验证IP格式
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        ip = '0.0.0.0'  # 如果IP格式不正确，使用默认值
    
    # 获取用户信息
    username = 'anonymous'
    if user:
        username = user.username
    elif request.user and request.user.is_authenticated:
        username = request.user.username
    
    # 获取请求路径
    path = request.path
    
    # 构建额外数据
    log_data = {
        'user': username,
        'ip': ip,
        'path': path,
        'event_type': event_type,
        'timestamp': now().isoformat(),
    }
    
    # 添加额外数据
    if additional_data:
        log_data.update(additional_data)
    
    # 记录安全事件
    security_logger.info(
        f"{event_type}: {message}", 
        extra={
            'user': username,
            'ip': ip,
            'path': path
        }
    )
    
    # 如果是认证事件，同时记录到认证日志
    if event_type in ['login', 'login_failed', 'logout', 'register', 'password_change']:
        auth_logger.info(
            f"{event_type}: {message}",
            extra={
                'user': username,
                'ip': ip,
                'path': path
            }
        )
    
    return log_data

def log_login_attempt(request, success, username, user=None):
    """记录登录尝试"""
    event_type = 'login' if success else 'login_failed'
    message = f"User '{username}' login {'successful' if success else 'failed'}"
    return log_security_event(request, event_type, message, user)

def log_registration(request, success, username, error=None):
    """记录注册尝试"""
    event_type = 'register' if success else 'register_failed'
    message = f"User '{username}' registration {'successful' if success else 'failed'}"
    if error:
        message += f" - {error}"
    return log_security_event(request, event_type, message)

def log_auth_action(request, action_type, message, user=None):
    """记录认证相关操作，如密码重置、令牌刷新等"""
    return log_security_event(request, action_type, message, user)

def log_security_violation(request, violation_type, details, user=None):
    """记录安全违规行为，如CSRF攻击尝试、XSS尝试等"""
    message = f"Security violation detected: {details}"
    return log_security_event(request, f"security_violation_{violation_type}", message, user) 