from rest_framework.permissions import BasePermission

class IsAuthenticatedExceptGet(BasePermission):
    """
    除了GET请求外，其他请求需要认证
    """
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user and request.user.is_authenticated 