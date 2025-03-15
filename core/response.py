from rest_framework.response import Response

class APIResponse(Response):
    """
    自定义API响应类，统一响应格式
    """
    def __init__(self, data=None, message="", code=200, status=None, **kwargs):
        response_data = {
            'status': 'success' if code < 400 else 'error',
            'code': code,
            'message': message,
        }
        
        if data is not None:
            response_data['data'] = data
            
        super().__init__(data=response_data, status=status, **kwargs) 