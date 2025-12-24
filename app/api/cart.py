"""
购物车API接口
处理基于Session的购物车操作
注意：购物车数据存储在Session中，不存储在数据库
"""

from flask import Blueprint

cart_bp = Blueprint('cart_api', __name__, url_prefix='/cart')

# TODO: 实现以下接口
# GET    /                   - 获取购物车
# POST   /add                - 添加到购物车
# PUT    /<item_id>          - 修改购物车项数量
# DELETE /<item_id>          - 删除购物车项
# DELETE /                   - 清空购物车
