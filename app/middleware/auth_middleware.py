"""
认证中间件
处理JWT Token验证和用户认证
"""



from flask import request, g
from functools import wraps
from app.utils.jwt_helper import verify_token
from app.utils.response import APIResponse

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        if not token:
            return {'success': False, 'message': '未登录或Token缺失'}, 401
        payload = verify_token(token)
        if not payload or 'user_id' not in payload:
            return {'success': False, 'message': 'Token无效或已过期'}, 401
        g.user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated_function

def register_auth_middleware(app):
    @app.before_request
    def inject_user():
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        if token:
            payload = verify_token(token)
            if payload and 'user_id' in payload:
                g.user_id = payload['user_id']

def auth_required(func):
    """登录认证装饰器"""
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return APIResponse.auth_error(message='请先登录')
        
        payload = verify_token(token)
        if not payload:
            return APIResponse.auth_error(message='Token无效或已过期')
        
        g.user_id = payload.get('user_id')
        return func(*args, **kwargs)
    return wrapper