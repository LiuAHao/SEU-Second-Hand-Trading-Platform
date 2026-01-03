"""
自定义装饰器
用于权限检查、日志记录、错误处理等
"""

from functools import wraps
from flask import request, g, jsonify
import re


def require_auth(f):
    """
    要求JWT认证的装饰器
    
    使用方法:
        @app.route('/api/profile')
        @require_auth
        def get_profile():
            user_id = g.current_user_id
            # ...
    """
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
    from app.models import User
    from app.utils.response import APIResponse
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(g, 'current_user_id', None)
        if not user_id:
            return APIResponse.auth_error(message='未认证，无法校验管理员权限')
        user = User.query.get(user_id)
        if not user or not getattr(user, 'is_admin', False):
            return APIResponse.permission_error(message='无管理员权限')
        return f(*args, **kwargs)
    
    return decorated_function


def handle_errors(f):
    """错误处理装饰器"""
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


def validate_request(schema):
    """
    请求参数验证装饰器
    
    Args:
        schema: 验证规则字典
            {
                'field_name': {
                    'type': 'string' | 'integer' | 'float' | 'boolean' | 'list' | 'dict',
                    'required': True | False,
                    'min': 1,              # 最小值（数字类型）
                    'max': 100,            # 最大值（数字类型）
                    'minlength': 1,        # 最小长度（字符串/列表）
                    'maxlength': 255,      # 最大长度（字符串/列表）
                    'allowed': ['value1', 'value2'],  # 允许的值列表
                    'regex': r'^[a-zA-Z0-9_]+$',  # 正则表达式
                    'schema': {...},       # 嵌套验证（用于list/dict类型）
                    'nullable': False,     # 是否允许为null
                    'default': 'value'     # 默认值
                }
            }
    
    使用示例:
        @app.route('/api/users', methods=['POST'])
        @validate_request({
            'username': {
                'type': 'string',
                'required': True,
                'minlength': 3,
                'maxlength': 50,
                'regex': r'^[a-zA-Z0-9_]+$'
            },
            'age': {
                'type': 'integer',
                'required': False,
                'min': 0,
                'max': 150,
                'default': 18
            }
        })
        def create_user():
            data = request.get_json()
            # 数据已经过验证
            # ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查请求内容类型
            if not request.is_json:
                from app.utils.response import APIResponse
                return APIResponse.validation_error(
                    errors={"general": "Content-Type必须是application/json"},
                    message="请求必须是JSON格式"
                )
            
            data = request.get_json()
            if data is None:
                data = {}
            
            errors = {}
            
            for field_name, rules in schema.items():
                # 检查字段是否存在
                value = data.get(field_name)
                
                # 检查是否必需
                if rules.get('required', False) and value is None:
                    errors[field_name] = f"字段 '{field_name}' 是必需的"
                    continue
                
                # 如果值为None且不是必需的，应用默认值或跳过
                if value is None:
                    if 'default' in rules:
                        data[field_name] = rules['default']
                        value = rules['default']
                    elif not rules.get('required', False):
                        continue
                
                # 检查是否可为null
                if value is None and not rules.get('nullable', False):
                    errors[field_name] = f"字段 '{field_name}' 不能为null"
                    continue
                
                # 验证类型
                if 'type' in rules:
                    type_errors = _validate_type(field_name, value, rules)
                    if type_errors:
                        errors[field_name] = type_errors
                        continue
                
                # 验证数字范围
                if rules.get('type') in ['integer', 'float', 'number']:
                    num_errors = _validate_number(field_name, value, rules)
                    if num_errors:
                        errors[field_name] = num_errors
                        continue
                
                # 验证字符串长度
                if rules.get('type') == 'string' and isinstance(value, str):
                    str_errors = _validate_string(field_name, value, rules)
                    if str_errors:
                        errors[field_name] = str_errors
                        continue
                
                # 验证列表长度
                if rules.get('type') == 'list' and isinstance(value, list):
                    list_errors = _validate_list(field_name, value, rules)
                    if list_errors:
                        errors[field_name] = list_errors
                        continue
                
                # 验证允许的值
                if 'allowed' in rules:
                    if value not in rules['allowed']:
                        allowed_values = ', '.join([str(v) for v in rules['allowed']])
                        errors[field_name] = f"必须是以下值之一: {allowed_values}"
                        continue
                
                # 验证正则表达式
                if 'regex' in rules and isinstance(value, str):
                    if not re.match(rules['regex'], value):
                        errors[field_name] = f"不符合格式要求"
                        continue
                
                # 嵌套验证（字典类型）
                if rules.get('type') == 'dict' and isinstance(value, dict):
                    if 'schema' in rules:
                        nested_errors = _validate_dict(field_name, value, rules['schema'])
                        if nested_errors:
                            errors[field_name] = nested_errors
                            continue
                
                # 嵌套验证（列表类型）
                if rules.get('type') == 'list' and isinstance(value, list):
                    if 'schema' in rules:
                        list_items_errors = _validate_list_items(field_name, value, rules['schema'])
                        if list_items_errors:
                            errors[field_name] = list_items_errors
                            continue
            
            # 如果有验证错误，返回错误响应
            if errors:
                from app.utils.response import APIResponse
                return APIResponse.validation_error(
                    errors=errors,
                    message="参数验证失败"
                )
            
            # 将验证后的数据存入g对象，以便在视图函数中使用
            g.validated_data = data
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def _validate_type(field_name, value, rules):
    """验证类型"""
    expected_type = rules['type']
    
    type_map = {
        'string': str,
        'integer': int,
        'float': (float, int),  # int也接受，因为可以自动转换
        'number': (int, float),
        'boolean': bool,
        'list': list,
        'dict': dict
    }
    
    expected_types = type_map.get(expected_type)
    if not expected_types:
        return None
    
    if not isinstance(expected_types, tuple):
        expected_types = (expected_types,)
    
    # 检查类型
    if not isinstance(value, expected_types):
        # 尝试类型转换（对于数字类型）
        if expected_type in ['integer', 'float', 'number']:
            try:
                if expected_type == 'integer':
                    int(value)
                else:
                    float(value)
            except (ValueError, TypeError):
                return f"必须是{expected_type}类型"
        else:
            return f"必须是{expected_type}类型"
    
    return None


def _validate_number(field_name, value, rules):
    """验证数字范围"""
    try:
        num_value = float(value) if rules.get('type') == 'float' else int(value)
    except (ValueError, TypeError):
        return "不是有效的数字"
    
    if 'min' in rules and num_value < rules['min']:
        return f"必须大于或等于 {rules['min']}"
    
    if 'max' in rules and num_value > rules['max']:
        return f"必须小于或等于 {rules['max']}"
    
    return None


def _validate_string(field_name, value, rules):
    """验证字符串"""
    if not isinstance(value, str):
        return "必须是字符串类型"
    
    if 'minlength' in rules and len(value) < rules['minlength']:
        return f"长度必须至少为 {rules['minlength']} 个字符"
    
    if 'maxlength' in rules and len(value) > rules['maxlength']:
        return f"长度不能超过 {rules['maxlength']} 个字符"
    
    return None


def _validate_list(field_name, value, rules):
    """验证列表"""
    if not isinstance(value, list):
        return "必须是列表类型"
    
    if 'minlength' in rules and len(value) < rules['minlength']:
        return f"必须至少包含 {rules['minlength']} 个元素"
    
    if 'maxlength' in rules and len(value) > rules['maxlength']:
        return f"不能超过 {rules['maxlength']} 个元素"
    
    return None


def _validate_dict(field_name, value, schema):
    """验证字典嵌套结构"""
    if not isinstance(value, dict):
        return "必须是字典类型"
    
    errors = {}
    for sub_field_name, sub_rules in schema.items():
        sub_value = value.get(sub_field_name)
        
        if sub_rules.get('required', False) and sub_value is None:
            errors[sub_field_name] = f"字段 '{sub_field_name}' 是必需的"
            continue
        
        # 简化版本：只做基本的类型检查
        if 'type' in sub_rules:
            type_error = _validate_type(sub_field_name, sub_value, sub_rules)
            if type_error:
                errors[sub_field_name] = type_error
    
    if errors:
        return errors
    
    return None


def _validate_list_items(field_name, value, schema):
    """验证列表中的每个元素"""
    if not isinstance(value, list):
        return "必须是列表类型"
    
    errors = {}
    for i, item in enumerate(value):
        if 'type' in schema:
            if schema['type'] == 'dict' and isinstance(item, dict):
                # 验证字典项
                if 'schema' in schema:
                    item_errors = _validate_dict(f"{field_name}[{i}]", item, schema['schema'])
                    if item_errors:
                        errors[f"{field_name}[{i}]"] = item_errors
            else:
                # 验证基本类型项
                type_error = _validate_type(f"{field_name}[{i}]", item, schema)
                if type_error:
                    errors[f"{field_name}[{i}]"] = type_error
    
    if errors:
        return errors
    
    return None


# ==================== 日志装饰器 ====================

def log_request(f):
    """记录请求日志的装饰器"""
    import logging
    import time
    
    logger = logging.getLogger(__name__)
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # 记录请求信息
        request_info = {
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string[:100] if request.user_agent else 'Unknown'
        }
        
        logger.info(f"Request started: {request_info}")
        
        try:
            response = f(*args, **kwargs)
            elapsed_time = (time.time() - start_time) * 1000  # 毫秒
            
            # 记录响应信息
            logger.info(f"Request completed: {request.method} {request.path} - {elapsed_time:.2f}ms")
            
            return response
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error(f"Request failed: {request.method} {request.path} - {elapsed_time:.2f}ms - Error: {str(e)}")
            raise
    
    return decorated_function


# ==================== 缓存装饰器 ====================

def cache_response(ttl=300):
    """
    缓存响应装饰器
    Args:
        ttl: 缓存时间（秒），默认5分钟
    """
    # 这里使用简单的内存缓存，实际项目中可以使用Redis等
    import time
    _cache = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键：函数名 + 参数 + 查询参数
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}:{str(request.args)}"
            
            # 检查缓存
            if cache_key in _cache:
                cache_entry = _cache[cache_key]
                if time.time() - cache_entry['timestamp'] < ttl:
                    return cache_entry['response']
                else:
                    # 缓存过期
                    del _cache[cache_key]
            
            # 执行函数
            response = f(*args, **kwargs)
            
            # 缓存响应
            if response and hasattr(response, 'status_code') and response.status_code == 200:
                _cache[cache_key] = {
                    'response': response,
                    'timestamp': time.time()
                }
            
            return response
        
        return decorated_function
    
    return decorator