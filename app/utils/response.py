"""
统一API响应格式处理
所有API接口返回统一的JSON格式
严格遵循指定响应结构：code, message, data, timestamp
"""

import time
from typing import Any, Dict, Optional, List
from flask import jsonify, Response
import uuid


class APIResponse:
    """API响应类 - 严格遵循指定格式"""
    
    # 标准响应代码
    SUCCESS = 0
    ERROR = 1
    VALIDATION_ERROR = 2
    AUTH_ERROR = 3
    PERMISSION_ERROR = 4
    NOT_FOUND = 5
    SERVER_ERROR = 6
    
    # HTTP状态码映射
    HTTP_STATUS_MAP = {
        SUCCESS: 200,
        VALIDATION_ERROR: 400,
        AUTH_ERROR: 401,
        PERMISSION_ERROR: 403,
        NOT_FOUND: 404,
        SERVER_ERROR: 500,
        ERROR: 400  # 默认错误使用400
    }
    
    # 标准消息映射
    MESSAGE_MAP = {
        SUCCESS: "成功",
        ERROR: "请求失败",
        VALIDATION_ERROR: "参数验证失败",
        AUTH_ERROR: "认证失败",
        PERMISSION_ERROR: "权限不足",
        NOT_FOUND: "资源不存在",
        SERVER_ERROR: "服务器内部错误"
    }
    
    def __init__(self, 
                 code: int = SUCCESS,
                 message: str = "",
                 data: Any = None,
                 timestamp: Optional[int] = None):
        """
        初始化API响应
        仅保留必要字段：code, message, data, timestamp
        """
        self.code = code
        self.message = message or self.MESSAGE_MAP.get(code, "")
        # 确保data默认为空字典
        self.data = data if data is not None else {}
        # 时间戳使用Unix时间戳（整数类型）
        self.timestamp = timestamp or int(time.time())
    
    def to_dict(self) -> Dict:
        """转换为字典 - 严格返回指定的四个字段"""
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> Response:
        """转换为Flask JSON响应"""
        return jsonify(self.to_dict())
    
    def to_json_with_status(self) -> Response:
        """转换为带HTTP状态码的JSON响应"""
        http_status = self.HTTP_STATUS_MAP.get(self.code, 200)
        return jsonify(self.to_dict()), http_status
    
    @classmethod
    def success(cls, 
                data: Any = None,
                message: str = "") -> Response:
        """
        成功响应快捷方法
        将分页、元数据等信息整合到data中
        """
        return cls(
            code=cls.SUCCESS,
            message=message or cls.MESSAGE_MAP[cls.SUCCESS],
            data=data
        ).to_json_with_status()
    
    @classmethod
    def created(cls, 
                data: Any = None,
                message: str = "",
                location: Optional[str] = None) -> Response:
        """
        创建成功响应 (201 Created)
        将location信息整合到data中
        """
        # 整合location到data
        if location and data is None:
            response_data = {"location": location}
        elif location and isinstance(data, dict):
            response_data = {**data, "location": location}
        else:
            response_data = data
            
        return cls(
            code=cls.SUCCESS,
            message=message or "创建成功",
            data=response_data
        ).to_json_with_status()
    
    @classmethod
    def error(cls,
              message: str = "",
              code: int = ERROR,
              data: Any = None,
              http_status: Optional[int] = None) -> Response:
        """
        错误响应快捷方法
        将错误详情整合到data中
        """
        return cls(
            code=code,
            message=message or cls.MESSAGE_MAP.get(code, "请求失败"),
            data=data
        ).to_json_with_status()
    
    @classmethod
    def validation_error(cls,
                         errors: Dict,
                         message: str = "",
                         data: Any = None) -> Response:
        """
        参数验证错误响应
        将验证错误信息整合到data中
        """
        # 整合错误信息到data
        if data is None:
            response_data = {"errors": errors}
        elif isinstance(data, dict):
            response_data = {** data, "errors": errors}
        else:
            response_data = data
            
        return cls.error(
            message=message or cls.MESSAGE_MAP[cls.VALIDATION_ERROR],
            code=cls.VALIDATION_ERROR,
            data=response_data
        )
    
    @classmethod
    def auth_error(cls,
                   message: str = "",
                   data: Any = None) -> Response:
        """认证错误响应"""
        return cls.error(
            message=message or cls.MESSAGE_MAP[cls.AUTH_ERROR],
            code=cls.AUTH_ERROR,
            data=data
        )
    
    @classmethod
    def permission_error(cls,
                         message: str = "",
                         data: Any = None) -> Response:
        """权限错误响应"""
        return cls.error(
            message=message or cls.MESSAGE_MAP[cls.PERMISSION_ERROR],
            code=cls.PERMISSION_ERROR,
            data=data
        )
    
    @classmethod
    def not_found(cls,
                  message: str = "",
                  data: Any = None) -> Response:
        """资源不存在响应"""
        return cls.error(
            message=message or cls.MESSAGE_MAP[cls.NOT_FOUND],
            code=cls.NOT_FOUND,
            data=data
        )
    
    @classmethod
    def server_error(cls,
                     message: str = "",
                     errors: Optional[Dict] = None,
                     data: Any = None) -> Response:
        """服务器错误响应"""
        # 整合错误信息到data
        if data is None:
            response_data = {"errors": errors} if errors else None
        elif isinstance(data, dict) and errors:
            response_data = {**data, "errors": errors}
        else:
            response_data = data
            
        return cls.error(
            message=message or cls.MESSAGE_MAP[cls.SERVER_ERROR],
            code=cls.SERVER_ERROR,
            data=response_data
        )
    
    @classmethod
    def paginated(cls,
                  items: List,
                  total: int,
                  page: int = 1,
                  per_page: int = 20,
                  message: str = "") -> Response:
        """
        分页数据响应
        将分页信息整合到data中
        """
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
        }
        
        # 整合分页信息到data
        data = {
            "items": items,
            "pagination": pagination
        }
        
        return cls.success(
            data=data,
            message=message or "获取数据成功"
        )


# ============ 兼容性函数 ============

def api_response(code: int, message: str, data: Any = None, timestamp: Optional[int] = None) -> Dict:
    """
    统一的API响应格式（兼容旧代码）
    """
    response = APIResponse(
        code=code,
        message=message,
        data=data,
        timestamp=timestamp
    )
    return response.to_dict()


def api_success(message: str = "成功", data: Any = None) -> Dict:
    """快捷成功响应（兼容旧代码）"""
    return api_response(code=0, message=message, data=data)


def api_error(message: str, code: int = 1, data: Any = None) -> Dict:
    """快捷错误响应（兼容旧代码）"""
    return api_response(code=code, message=message, data=data)


# ============ 便捷函数 ============

def success_response(data: Any = None, message: str = "成功") -> Response:
    """快捷成功响应（返回Flask Response）"""
    return APIResponse.success(data=data, message=message)


def error_response(message: str = "请求失败", code: int = 1, 
                   errors: Optional[Dict] = None) -> Response:
    """快捷错误响应（返回Flask Response）"""
    # 整合错误信息到data
    data = {"errors": errors} if errors else None
    return APIResponse.error(message=message, code=code, data=data)


def validation_response(errors: Dict, message: str = "参数验证失败") -> Response:
    """参数验证错误响应"""
    return APIResponse.validation_error(errors=errors, message=message)


def auth_response(message: str = "认证失败") -> Response:
    """认证错误响应"""
    return APIResponse.auth_error(message=message)


def not_found_response(message: str = "资源不存在") -> Response:
    """资源不存在响应"""
    return APIResponse.not_found(message=message)


def paginated_response(items: List, total: int, page: int = 1, 
                       per_page: int = 20, message: str = "") -> Response:
    """分页响应"""
    return APIResponse.paginated(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        message=message
    )


# ============ 装饰器 ============

def handle_api_errors(func):
    """API错误处理装饰器"""
    from functools import wraps
    import traceback
    import logging
    
    logger = logging.getLogger(__name__)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # 业务逻辑错误
            logger.warning(f"业务逻辑错误: {str(e)}")
            return error_response(message=str(e), code=APIResponse.VALIDATION_ERROR)
        except PermissionError as e:
            # 权限错误
            logger.warning(f"权限错误: {str(e)}")
            return error_response(message=str(e), code=APIResponse.PERMISSION_ERROR)
        except Exception as e:
            # 未捕获的异常
            logger.error(f"未捕获的异常: {str(e)}\n{traceback.format_exc()}")
            return error_response(
                message="服务器内部错误，请稍后重试",
                code=APIResponse.SERVER_ERROR
            )
    
    return wrapper