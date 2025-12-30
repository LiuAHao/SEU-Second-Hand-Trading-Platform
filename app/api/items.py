"""
商品管理路由层
对应 API.item 所有接口
"""
from flask import Blueprint, request, g
from app.utils.response import APIResponse
from app.services.item_service import ItemService
from app.middleware.auth_middleware import auth_required

items_bp = Blueprint('items', __name__, url_prefix='/api/item')

# -------------------------- 1. 获取首页推荐商品 --------------------------
@items_bp.route('/getFeatured', methods=['POST'])
def get_featured():
    """API.item.getFeatured 接口实现"""
    data = request.json or {}
    limit = data.get('limit', 12)

    # 验证limit参数
    if not isinstance(limit, int) or limit <= 0:
        limit = 12

    # 调用服务层
    result = ItemService.get_featured_items(limit)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='获取成功',
        data=result['data']
    )

# -------------------------- 2. 搜索商品 --------------------------
@items_bp.route('/search', methods=['POST'])
def search():
    """API.item.search 接口实现"""
    data = request.json or {}
    query = data.get('query', '').strip()
    search_type = data.get('type', 'title').strip()
    page = data.get('page', 1)
    limit = data.get('limit', 12)
    category = data.get('category', '').strip()
    min_price = data.get('minPrice', None)
    max_price = data.get('maxPrice', None)
    sort = data.get('sort', 'latest').strip()

    # 验证分页参数
    if not isinstance(page, int) or page <= 0:
        page = 1
    if not isinstance(limit, int) or limit <= 0:
        limit = 12

    # 验证搜索类型和排序方式
    valid_search_types = ['title', 'seller', 'category']
    valid_sorts = ['latest', 'popular', 'price-asc', 'price-desc']
    if search_type not in valid_search_types:
        search_type = 'title'
    if sort not in valid_sorts:
        sort = 'latest'

    # 调用服务层
    result = ItemService.search_items(
        query=query,
        search_type=search_type,
        page=page,
        limit=limit,
        category=category if category else None,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='搜索成功',
        data=result['data']
    )

# -------------------------- 3. 按分类获取商品 --------------------------
@items_bp.route('/getByCategory/<category>', methods=['POST'])
def get_by_category(category):
    """API.item.getByCategory 接口实现"""
    data = request.json or {}
    page = data.get('page', 1)
    limit = data.get('limit', 12)

    # 验证分页参数
    if not isinstance(page, int) or page <= 0:
        page = 1
    if not isinstance(limit, int) or limit <= 0:
        limit = 12

    # 调用服务层
    result = ItemService.get_items_by_category(category, page, limit)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='获取成功',
        data=result['data']
    )

# -------------------------- 4. 获取商品详情 --------------------------
@items_bp.route('/getDetail/<int:item_id>', methods=['GET'])
def get_detail(item_id):
    """API.item.getDetail 接口实现"""
    # 调用服务层
    result = ItemService.get_item_detail(item_id)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='获取成功',
        data=result['data']
    )

# -------------------------- 5. 发布新商品 --------------------------
@items_bp.route('/create', methods=['POST'])
@auth_required
def create():
    """API.item.create 接口实现"""
    user_id = g.user_id
    item_data = request.json or {}

    # 调用服务层
    result = ItemService.create_item(user_id, item_data)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='发布成功',
        data=result['data']
    )

# -------------------------- 6. 更新商品 --------------------------
@items_bp.route('/update/<int:item_id>', methods=['POST'])
@auth_required
def update(item_id):
    """API.item.update 接口实现"""
    user_id = g.user_id
    item_data = request.json or {}

    # 调用服务层
    result = ItemService.update_item(item_id, user_id, item_data)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='更新成功',
        data=result['data']
    )

# -------------------------- 7. 删除商品 --------------------------
@items_bp.route('/delete/<int:item_id>', methods=['POST'])
@auth_required
def delete(item_id):
    """API.item.delete 接口实现"""
    user_id = g.user_id

    # 调用服务层
    result = ItemService.delete_item(item_id, user_id)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message=result['message'],
        data={}
    )

# -------------------------- 8. 检查商品库存 --------------------------
@items_bp.route('/checkStock', methods=['POST'])
def check_stock():
    """API.item.checkStock 接口实现"""
    item_list = request.json or []

    # 调用服务层
    result = ItemService.check_stock(item_list)
    if not result['success']:
        return APIResponse.error(message=result['message'])

    # 返回成功响应
    return APIResponse.success(
        message='检查成功',
        data=result['data']
    )