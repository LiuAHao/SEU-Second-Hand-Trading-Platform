"""
商品管理API接口
处理商品的CRUD操作、搜索、分类浏览等
"""

from flask import Blueprint

items_bp = Blueprint('items_api', __name__, url_prefix='/items')

# TODO: 实现以下接口
# POST   /                   - 发布新商品
# GET    /featured           - 获取首页推荐商品
# GET    /search             - 搜索商品
# GET    /category/<cat>     - 按分类获取商品
# GET    /<item_id>          - 获取商品详情
# PUT    /<item_id>          - 更新商品信息
# DELETE /<item_id>          - 删除商品
# POST   /check-stock        - 批量检查库存
