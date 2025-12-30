"""
用户管理路由层
对应 API.user.getCurrentUser / getUserProfile / updateProfile 等接口
"""
from flask import Blueprint, request, g
from app.utils.response import APIResponse
from app.services.user_service import UserService
from app.middleware.auth_middleware import auth_required

users_bp = Blueprint('users', __name__, url_prefix='/api/user')

# -------------------------- 4. 获取当前用户信息 --------------------------
@users_bp.route('/getCurrentUser', methods=['GET'])
@auth_required
def get_current_user():
    """API.user.getCurrentUser 接口实现"""
    # 从g对象获取当前用户ID
    user_id = g.user_id

    # 调用服务层获取用户信息
    result = UserService.get_current_user(user_id)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='获取成功',
        data=result['data']
    )

# -------------------------- 5. 获取用户资料 --------------------------
@users_bp.route('/getUserProfile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """API.user.getUserProfile 接口实现"""
    # 调用服务层获取用户公开资料
    result = UserService.get_user_profile(user_id)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='获取成功',
        data=result['data']
    )

# -------------------------- 6. 更新个人资料 --------------------------
@users_bp.route('/updateProfile', methods=['POST'])
@auth_required
def update_profile():
    """API.user.updateProfile 接口实现"""
    user_id = g.user_id
    profile_data = request.json or {}

    # 调用服务层更新资料
    result = UserService.update_user_profile(user_id, profile_data)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='更新成功',
        data=result['data']
    )

# -------------------------- 7. 检查用户名可用性 --------------------------
@users_bp.route('/checkUsername/<username>', methods=['GET'])
def check_username(username):
    """API.user.checkUsername 接口实现"""
    # 调用服务层检查用户名
    result = UserService.check_username_available(username)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='查询成功',
        data=result['data']
    )

# -------------------------- 8. 检查邮箱可用性 --------------------------
@users_bp.route('/checkEmail/<email>', methods=['GET'])
def check_email(email):
    """API.user.checkEmail 接口实现"""
    # 调用服务层检查邮箱
    result = UserService.check_email_available(email)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='查询成功',
        data=result['data']
    )