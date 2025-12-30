"""
自定义装饰器
用于权限检查、日志记录、错误处理等
"""

from functools import wraps


def require_auth(f):
    """
    要求JWT认证的装饰器
    TODO: 实现认证检查
    
    使用方法:
        @app.route('/api/profile')
        @require_auth
        def get_profile():
            user_id = g.current_user_id
            # ...
    """
    from flask import request, g, jsonify
    from app.utils.jwt_helper import verify_token
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'code': 401, 'message': '未认证，无效Token'}), 401
        token = auth_header.split(' ')[1]
        payload = verify_token(token)
        if not payload or 'user_id' not in payload:
            return jsonify({'code': 401, 'message': 'Token无效或过期'}), 401
        g.current_user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """管理员权限检查装饰器（可选）"""
    from flask import g, jsonify
    from app.models import User
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(g, 'current_user_id', None)
        if not user_id:
            return jsonify({'code': 403, 'message': '未认证，无法校验管理员权限'}), 403
        user = User.query.get(user_id)
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({'code': 403, 'message': '无管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function


def handle_errors(f):
    """错误处理装饰器"""
    from flask import jsonify
    from app.utils.response import APIResponse
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return APIResponse.validation_error(
                errors={"general": str(e)},
                message=f'参数错误: {str(e)}'
            )
        except Exception as e:
            import traceback
            print(f"未捕获的异常: {str(e)}\n{traceback.format_exc()}")
            return APIResponse.server_error(
                message=f'服务器错误: {str(e)}'
            )
    return decorated_function