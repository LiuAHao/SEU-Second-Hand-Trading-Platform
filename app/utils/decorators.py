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
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: 验证JWT Token
        # TODO: 将user_id注入到g对象
        pass
    
    return decorated_function


def require_admin(f):
    """管理员权限检查装饰器（可选）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: 检查用户是否为管理员
        pass
    
    return decorated_function


def handle_errors(f):
    """错误处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # TODO: 执行被装饰函数
            pass
        except ValueError as e:
            # TODO: 处理值错误
            pass
        except Exception as e:
            # TODO: 处理其他异常
            pass
    
    return decorated_function
