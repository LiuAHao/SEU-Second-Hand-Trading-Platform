"""
评价与推荐API接口
处理用户评价、商品推荐等
"""

from flask import Blueprint

reviews_bp = Blueprint('reviews_api', __name__, url_prefix='/reviews')

# TODO: 实现以下接口
# GET    /<item_id>          - 获取商品评价列表
# POST   /                   - 创建评价
# GET    /recommend/popular  - 获取热销商品
# GET    /recommend/latest   - 获取最新商品
# GET    /users/<user_id>/rating - 获取用户评分
