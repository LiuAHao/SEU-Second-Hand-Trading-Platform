"""
用户信息API接口
处理用户资料的获取和更新
"""

from flask import Blueprint

users_bp = Blueprint('users_api', __name__, url_prefix='/users')

# TODO: 实现以下接口
# GET    /current            - 获取当前用户信息
# GET    /<user_id>/profile  - 获取用户资料
# PUT    /profile            - 更新个人资料
