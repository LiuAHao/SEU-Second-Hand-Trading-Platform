"""
用户认证API接口
处理注册、登录、登出等认证相关的请求
"""

from flask import Blueprint

auth_bp = Blueprint('auth_api', __name__, url_prefix='/auth')

# TODO: 实现以下接口
# POST   /register           - 用户注册
# POST   /login              - 用户登录
# POST   /logout             - 用户登出
# GET    /check-username     - 检查用户名可用性
# GET    /check-email        - 检查邮箱可用性
