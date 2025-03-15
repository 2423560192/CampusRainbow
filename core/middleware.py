from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

class ResponseFormatMiddleware(MiddlewareMixin):
    """
    响应格式统一中间件
    """
    def process_response(self, request, response):
        # 如果已经是JsonResponse或者是文件下载等特殊响应，则不处理
        if isinstance(response, JsonResponse) or response.get('Content-Type', '').startswith(('application/octet-stream', 'image/', 'video/')):
            return response
            
        # 如果是API请求且不是成功的响应
        if request.path.startswith('/api/') and response.status_code != 200:
            response_data = {
                'status': 'error',
                'code': response.status_code,
                'message': response.reason_phrase
            }
            return JsonResponse(response_data, status=response.status_code)
            
        return response 