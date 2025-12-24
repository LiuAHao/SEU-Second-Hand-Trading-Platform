"""
订单与结账API接口
处理订单创建、查询、取消等操作（最复杂，涉及事务处理）
"""

from flask import Blueprint

orders_bp = Blueprint('orders_api', __name__, url_prefix='/orders')

# TODO: 实现以下接口
# POST   /                   - 创建订单 (关键：事务处理、库存扣减)
# GET    /                   - 获取订单列表
# GET    /<order_id>         - 获取订单详情
# PUT    /<order_id>/status  - 更新订单状态
# DELETE /<order_id>         - 取消订单
# GET    /addresses          - 获取配送地址列表
# POST   /addresses          - 添加配送地址
# PUT    /addresses/<addr_id> - 更新配送地址
