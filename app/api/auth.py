
"""
用户认证路由层
对应 API.user.register / login / logout 接口
"""
from flask import Blueprint, request
from app.utils.response import APIResponse
from app.services.user_service import UserService
from app.middleware.auth_middleware import auth_required
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/user')

# -------------------------- 1. 用户注册 --------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    API.user.register 接口实现
    请求参数：username/email/password
    响应：用户ID/用户名/邮箱
    """
    data = request.json or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    # 参数格式验证
    errors = {}
    # 用户名验证：3-16字符，仅限字母/数字/下划线
    if not username:
        errors['username'] = '用户名不能为空'
    elif not re.match(r'^[a-zA-Z0-9_]{3,16}$', username):
        errors['username'] = '用户名需3-16字符，仅限字母、数字、下划线'

    # 邮箱验证：必须以@seu.edu.cn结尾
    if not email:
        errors['email'] = '邮箱不能为空'
    elif not email.endswith('@seu.edu.cn'):
        errors['email'] = '邮箱必须为@seu.edu.cn格式'

    # 密码验证：8+字符，包含大小写和数字
    if not password:
        errors['password'] = '密码不能为空'
    elif len(password) < 8:
        errors['password'] = '密码长度不能少于8位'
    elif not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password):
        errors['password'] = '密码需包含大小写字母和数字'

    # 验证失败返回错误
    if errors:
        return APIResponse.validation_error(errors=errors)

    # 调用服务层处理注册
    result = UserService.register_user(username, email, password)
    if not result['success']:
        return APIResponse.error(message=result['message'], code=400)

    # 返回成功响应
    return APIResponse.success(
        message='注册成功',
        data=result['data']
    )

# -------------------------- 2. 用户登录 --------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    API.user.login 接口实现
    请求参数：username/password（username可为用户名或邮箱）
    响应：token + 用户信息
    """
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    # 参数验证
    if not username:
        return APIResponse.validation_error(errors={'username': '用户名或邮箱不能为空'})
    if not password:
        return APIResponse.validation_error(errors={'password': '密码不能为空'})

    # 调用服务层处理登录
    result = UserService.login_user(username, password)
    if not result['success']:
        return APIResponse.auth_error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='登录成功',
        data=result['data']
    )

# -------------------------- 3. 用户登出 --------------------------
@auth_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    """
    API.user.logout 接口实现
    注：前端可自行清除Token，后端无需额外处理，仅返回成功响应
    """
    # 若需后端实现Token黑名单，可在此处添加逻辑
    return APIResponse.success(
        message='登出成功',
        data={}
    )