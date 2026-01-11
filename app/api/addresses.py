"""
收货地址 API
"""
from flask import Blueprint, request, g
from app.utils.response import APIResponse
from app.middleware.auth_middleware import auth_required
from app.services.order_service import OrderService

addresses_bp = Blueprint('addresses', __name__, url_prefix='/api/addresses')


@addresses_bp.route('', methods=['GET'])
@auth_required
def list_addresses():
    """获取当前用户的收货地址列表"""
    success, data = OrderService.get_addresses(g.user_id)
    if not success:
        return APIResponse.error(message=data)
    return APIResponse.success(data={'items': data})


@addresses_bp.route('', methods=['POST'])
@auth_required
def create_address():
    """创建新的收货地址"""
    payload = request.json or {}
    success, data = OrderService.create_address(g.user_id, payload)
    if not success:
        return APIResponse.error(message=data)
    return APIResponse.success(data=data)


@addresses_bp.route('/<int:address_id>', methods=['PUT'])
@auth_required
def update_address(address_id):
    """更新收货地址"""
    payload = request.json or {}
    success, data = OrderService.update_address(g.user_id, address_id, payload)
    if not success:
        return APIResponse.error(message=data)
    return APIResponse.success(data=data)


@addresses_bp.route('/<int:address_id>', methods=['DELETE'])
@auth_required
def delete_address(address_id):
    """删除收货地址"""
    success, data = OrderService.delete_address(g.user_id, address_id)
    if not success:
        return APIResponse.error(message=data)
    return APIResponse.success(message=data)


@addresses_bp.route('/<int:address_id>/default', methods=['POST'])
@auth_required
def set_default(address_id):
    """设置默认收货地址"""
    success, data = OrderService.update_address(g.user_id, address_id, {'is_default': True})
    if not success:
        return APIResponse.error(message=data)
    return APIResponse.success(data=data)
