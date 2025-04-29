from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    """
    限制登录尝试的频率
    匿名用户每分钟只能尝试5次登录
    """
    rate = '5/minute'
    scope = 'login'

class SensitiveOperationRateThrottle(UserRateThrottle):
    """
    限制敏感操作（如密码重置、个人信息更新）的频率
    认证用户每小时只能进行10次敏感操作
    """
    rate = '10/hour'
    scope = 'sensitive'

class RegisterRateThrottle(AnonRateThrottle):
    """
    限制注册操作的频率
    同一IP每天只能注册5个账户
    """
    rate = '5/day'
    scope = 'register'

class BurstRateThrottle(UserRateThrottle):
    """
    应对突发流量的节流策略
    允许用户短时间内进行较多请求，但限制总量
    """
    rate = '50/minute'
    scope = 'burst' 