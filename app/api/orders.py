"""
订单与结账API接口
处理订单创建、查询、取消等操作（最复杂，涉及事务处理）
"""

from flask import Blueprint, request, g
from app.services.order_service import OrderService
from app.middleware.auth_middleware import auth_required
from app.utils.decorators import validate_request
from app.utils.response import success_response, error_response, validation_response, not_found_response

orders_bp = Blueprint('orders_api', __name__, url_prefix='/orders')


@orders_bp.route('/', methods=['POST'])
@auth_required
@validate_request({
    'items': {
        'type': 'list',
        'required': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'item_id': {'type': 'integer', 'required': True, 'min': 1},
                'quantity': {'type': 'integer', 'required': True, 'min': 1, 'max': 100}
            }
        },
        'minlength': 1
    },
    'address_id': {'type': 'integer', 'required': True, 'min': 1}
})
def create_order():
    """
    创建订单
    POST /orders/
    
    请求体：
    {
        "items": [
            {"item_id": 1, "quantity": 2},
            {"item_id": 2, "quantity": 1}
        ],
        "address_id": 123
    }
    
    响应：
    {
        "code": 0,
        "message": "成功",
        "data": {
            "order_id": 1,
            "total_amount": 150.00,
            "status": "pending",
            "shipping_address": "南京市玄武区四牌楼2号",
            "created_at": "2024-01-15T10:30:00",
            "items_count": 2
        },
        "timestamp": 1705300200
    }
    """
    try:
        data = request.get_json()
        buyer_id = g.user_id  # 从g对象获取用户ID
        
        # 调用订单服务创建订单
        success, result = OrderService.create_order(
            buyer_id=buyer_id,
            items_data=data['items'],
            address_id=data['address_id']
        )
        
        if success:
            return success_response(
                data=result,
                message="订单创建成功"
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"创建订单失败: {str(e)}",
            code=500
        )


@orders_bp.route('/', methods=['GET'])
@auth_required
def get_orders_list():
    """
    获取用户订单列表
    GET /orders/?page=1&limit=10
    
    查询参数：
    - page: 页码，默认1
    - limit: 每页数量，默认10
    
    响应：
    {
        "code": 0,
        "message": "成功",
        "data": {
            "orders": [
                {
                    "id": 1,
                    "total_amount": 150.00,
                    "status": "pending",
                    "status_text": "待支付",
                    "shipping_address": "南京市玄武区四牌楼2号",
                    "created_at": "2024-01-15T10:30:00",
                    "updated_at": "2024-01-15T10:30:00",
                    "items": [
                        {
                            "item_id": 1,
                            "title": "二手教材",
                            "quantity": 2,
                            "price": 50.00,
                            "image_url": "http://example.com/image.jpg"
                        }
                    ],
                    "items_count": 1
                }
            ],
            "pagination": {
                "page": 1,
                "limit": 10,
                "total": 25,
                "total_pages": 3
            }
        },
        "timestamp": 1705300200
    }
    """
    try:
        # 从g对象获取用户ID
        buyer_id = g.user_id
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # 参数验证
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # 调用订单服务获取订单列表
        success, result = OrderService.get_orders(
            buyer_id=buyer_id,
            page=page,
            limit=limit
        )
        
        if success:
            return success_response(
                data=result,
                message="获取订单列表成功"
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"获取订单列表失败: {str(e)}",
            code=500
        )


@orders_bp.route('/<int:order_id>', methods=['GET'])
@auth_required
def get_order_detail(order_id):
    """
    获取订单详情
    GET /orders/{order_id}
    
    响应：
    {
        "code": 0,
        "message": "成功",
        "data": {
            "id": 1,
            "total_amount": 150.00,
            "status": "pending",
            "status_text": "待支付",
            "shipping_address": "南京市玄武区四牌楼2号",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00",
            "buyer": {
                "id": 123,
                "username": "张三",
                "phone": "13800138000"
            },
            "items": [
                {
                    "order_item_id": 1,
                    "item_id": 1,
                    "title": "二手教材",
                    "description": "九成新教材",
                    "quantity": 2,
                    "price_at_purchase": 50.00,
                    "subtotal": 100.00,
                    "image_url": "http://example.com/image.jpg",
                    "category": "books",
                    "seller_info": {
                        "id": 456,
                        "username": "李四"
                    }
                }
            ],
            "items_count": 1
        },
        "timestamp": 1705300200
    }
    """
    try:
        if order_id <= 0:
            return error_response(message="订单ID无效", code=400)
        
        # 从g对象获取用户ID
        buyer_id = g.user_id
        
        # 调用订单服务获取订单详情
        success, result = OrderService.get_order_detail(
            order_id=order_id,
            buyer_id=buyer_id
        )
        
        if success:
            return success_response(
                data=result,
                message="获取订单详情成功"
            )
        else:
            if "不存在" in result or "无权" in result:
                return not_found_response(message=result)
            else:
                return error_response(
                    message=result,
                    code=400
                )
                
    except Exception as e:
        return error_response(
            message=f"获取订单详情失败: {str(e)}",
            code=500
        )


@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@auth_required
@validate_request({
    'status': {'type': 'string', 'required': True, 'allowed': ['pending', 'paid', 'shipped', 'completed', 'cancelled']}
})
def update_order_status(order_id):
    """
    更新订单状态
    PUT /orders/{order_id}/status
    
    请求体：
    {
        "status": "cancelled"
    }
    
    响应：
    {
        "code": 0,
        "message": "订单状态更新成功",
        "data": null,
        "timestamp": 1705300200
    }
    """
    try:
        if order_id <= 0:
            return error_response(message="订单ID无效", code=400)
        
        data = request.get_json()
        status = data['status']
        
        # 从g对象获取用户ID
        buyer_id = g.user_id
        
        # 调用订单服务更新状态
        success, result = OrderService.update_order_status(
            order_id=order_id,
            buyer_id=buyer_id,
            status=status
        )
        
        if success:
            return success_response(
                data=None,
                message=result
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"更新订单状态失败: {str(e)}",
            code=500
        )


@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@auth_required
def cancel_order(order_id):
    """
    取消订单
    DELETE /orders/{order_id}
    
    响应：
    {
        "code": 0,
        "message": "订单取消成功，库存已恢复",
        "data": null,
        "timestamp": 1705300200
    }
    """
    try:
        if order_id <= 0:
            return error_response(message="订单ID无效", code=400)
        
        # 从g对象获取用户ID
        buyer_id = g.user_id
        
        # 调用订单服务取消订单
        success, result = OrderService.cancel_order(
            order_id=order_id,
            buyer_id=buyer_id
        )
        
        if success:
            return success_response(
                data=None,
                message=result
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"取消订单失败: {str(e)}",
            code=500
        )


@orders_bp.route('/addresses', methods=['GET'])
@auth_required
def get_addresses():
    """
    获取用户的配送地址列表
    GET /orders/addresses
    
    响应：
    {
        "code": 0,
        "message": "成功",
        "data": [
            {
                "id": 1,
                "recipient_name": "张三",
                "phone": "13800138000",
                "province": "江苏省",
                "city": "南京市",
                "district": "玄武区",
                "detail": "四牌楼2号",
                "is_default": true,
                "created_at": "2024-01-15T10:30:00",
                "full_address": "江苏省南京市玄武区四牌楼2号"
            }
        ],
        "timestamp": 1705300200
    }
    """
    try:
        # 从g对象获取用户ID
        user_id = g.user_id
        
        # 调用订单服务获取地址列表
        success, result = OrderService.get_addresses(user_id)
        
        if success:
            return success_response(
                data=result,
                message="获取地址列表成功"
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"获取地址列表失败: {str(e)}",
            code=500
        )


@orders_bp.route('/addresses', methods=['POST'])
@auth_required
@validate_request({
    'recipient_name': {'type': 'string', 'required': True, 'minlength': 1, 'maxlength': 50},
    'phone': {'type': 'string', 'required': True, 'minlength': 11, 'maxlength': 20},
    'province': {'type': 'string', 'required': False, 'maxlength': 50},
    'city': {'type': 'string', 'required': False, 'maxlength': 50},
    'district': {'type': 'string', 'required': False, 'maxlength': 50},
    'detail': {'type': 'string', 'required': True, 'minlength': 1, 'maxlength': 255},
    'is_default': {'type': 'boolean', 'required': False, 'default': False}
})
def create_address():
    """
    添加新配送地址
    POST /orders/addresses
    
    请求体：
    {
        "recipient_name": "张三",
        "phone": "13800138000",
        "province": "江苏省",
        "city": "南京市",
        "district": "玄武区",
        "detail": "四牌楼2号",
        "is_default": true
    }
    
    响应：
    {
        "code": 0,
        "message": "创建成功",
        "data": {
            "id": 1,
            "recipient_name": "张三",
            "phone": "13800138000",
            "province": "江苏省",
            "city": "南京市",
            "district": "玄武区",
            "detail": "四牌楼2号",
            "is_default": true
        },
        "timestamp": 1705300200
    }
    """
    try:
        data = request.get_json()
        
        # 从g对象获取用户ID
        user_id = g.user_id
        
        # 调用订单服务创建地址
        success, result = OrderService.create_address(user_id, data)
        
        if success:
            return success_response(
                data=result,
                message="地址创建成功"
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"创建地址失败: {str(e)}",
            code=500
        )


@orders_bp.route('/addresses/<int:address_id>', methods=['PUT'])
@auth_required
@validate_request({
    'recipient_name': {'type': 'string', 'required': False, 'minlength': 1, 'maxlength': 50},
    'phone': {'type': 'string', 'required': False, 'minlength': 11, 'maxlength': 20},
    'province': {'type': 'string', 'required': False, 'maxlength': 50},
    'city': {'type': 'string', 'required': False, 'maxlength': 50},
    'district': {'type': 'string', 'required': False, 'maxlength': 50},
    'detail': {'type': 'string', 'required': False, 'minlength': 1, 'maxlength': 255},
    'is_default': {'type': 'boolean', 'required': False}
})
def update_address(address_id):
    """
    更新配送地址
    PUT /orders/addresses/{address_id}
    
    请求体：
    {
        "recipient_name": "张三",
        "phone": "13800138000",
        "province": "江苏省",
        "city": "南京市",
        "district": "玄武区",
        "detail": "四牌楼2号",
        "is_default": true
    }
    
    响应：
    {
        "code": 0,
        "message": "更新成功",
        "data": {
            "id": 1,
            "recipient_name": "张三",
            "phone": "13800138000",
            "province": "江苏省",
            "city": "南京市",
            "district": "玄武区",
            "detail": "四牌楼2号",
            "is_default": true
        },
        "timestamp": 1705300200
    }
    """
    try:
        if address_id <= 0:
            return error_response(message="地址ID无效", code=400)
        
        data = request.get_json()
        
        # 从g对象获取用户ID
        user_id = g.user_id
        
        # 调用订单服务更新地址
        success, result = OrderService.update_address(user_id, address_id, data)
        
        if success:
            return success_response(
                data=result,
                message="地址更新成功"
            )
        else:
            if "不存在" in result or "无权" in result:
                return not_found_response(message=result)
            else:
                return error_response(
                    message=result,
                    code=400
                )
                
    except Exception as e:
        return error_response(
            message=f"更新地址失败: {str(e)}",
            code=500
        )


@orders_bp.route('/statistics', methods=['GET'])
@auth_required
def get_order_statistics():
    """
    获取用户的订单统计信息
    GET /orders/statistics
    
    响应：
    {
        "code": 0,
        "message": "成功",
        "data": {
            "total_orders": 10,
            "pending_orders": 2,
            "completed_orders": 7,
            "total_spent": 1250.50
        },
        "timestamp": 1705300200
    }
    """
    try:
        # 从g对象获取用户ID
        user_id = g.user_id
        
        # 调用订单服务获取统计信息
        success, result = OrderService.get_statistics(user_id)
        
        if success:
            return success_response(
                data=result,
                message="获取统计信息成功"
            )
        else:
            return error_response(
                message=result,
                code=400
            )
            
    except Exception as e:
        return error_response(
            message=f"获取统计信息失败: {str(e)}",
            code=500
        )


# ==================== 错误处理器 ====================
@orders_bp.errorhandler(400)
def handle_bad_request(error):
    """处理400错误"""
    return error_response(
        message="请求参数错误",
        code=400,
        errors={"details": str(error)}
    )


@orders_bp.errorhandler(404)
def handle_not_found(error):
    """处理404错误"""
    return not_found_response(message="订单资源不存在")


@orders_bp.errorhandler(500)
def handle_server_error(error):
    """处理500错误"""
    return error_response(
        message="服务器内部错误",
        code=500
    )