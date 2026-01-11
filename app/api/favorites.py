"""
收藏功能API接口
处理用户收藏商品的HTTP请求
"""
from flask import Blueprint, request, g
from app.utils.response import APIResponse
from app.middleware.auth_middleware import auth_required
from app.services.favorite_service import FavoriteService

favorites_bp = Blueprint('favorites_api', __name__, url_prefix='/api/favorites')


# -------------------------- 1. 添加收藏 --------------------------
@favorites_bp.route('/add/<int:item_id>', methods=['POST'])
@auth_required
def add_favorite(item_id):
    """添加商品到收藏"""
    try:
        success, message, favorite = FavoriteService.add_favorite(g.user_id, item_id)

        if success:
            return APIResponse.success(
                message=message,
                data={'favorite_id': favorite.id}
            )
        else:
            return APIResponse.error(message=message)

    except Exception as e:
        return APIResponse.server_error(message=f"添加收藏失败: {str(e)}")


# -------------------------- 2. 取消收藏 --------------------------
@favorites_bp.route('/remove/<int:item_id>', methods=['POST'])
@auth_required
def remove_favorite(item_id):
    """取消收藏商品"""
    try:
        success, message = FavoriteService.remove_favorite(g.user_id, item_id)

        if success:
            return APIResponse.success(message=message)
        else:
            return APIResponse.not_found(message=message)

    except Exception as e:
        return APIResponse.server_error(message=f"取消收藏失败: {str(e)}")


# -------------------------- 3. 切换收藏状态 --------------------------
@favorites_bp.route('/toggle/<int:item_id>', methods=['POST'])
@auth_required
def toggle_favorite(item_id):
    """切换收藏状态"""
    try:
        success, message, is_favorited = FavoriteService.toggle_favorite(g.user_id, item_id)

        if success:
            return APIResponse.success(
                message=message,
                data={'is_favorited': is_favorited}
            )
        else:
            return APIResponse.error(message=message)

    except Exception as e:
        return APIResponse.server_error(message=f"操作失败: {str(e)}")


# -------------------------- 4. 检查是否已收藏 --------------------------
@favorites_bp.route('/check/<int:item_id>', methods=['GET'])
@auth_required
def check_favorite(item_id):
    """检查是否已收藏某个商品"""
    try:
        is_favorited = FavoriteService.check_favorite(g.user_id, item_id)

        return APIResponse.success(
            message='获取成功',
            data={'is_favorited': is_favorited}
        )

    except Exception as e:
        return APIResponse.server_error(message=f"检查失败: {str(e)}")


# -------------------------- 5. 获取用户收藏列表 --------------------------
@favorites_bp.route('/list', methods=['GET'])
@auth_required
def get_favorite_list():
    """获取用户收藏列表（带商品详情）"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # 验证分页参数
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20

        # 获取收藏列表
        items, total = FavoriteService.get_favorite_items(g.user_id, page, limit)

        return APIResponse.success(
            message='获取成功',
            data={
                'items': items,
                'total': total,
                'page': page,
                'limit': limit
            }
        )

    except Exception as e:
        return APIResponse.server_error(message=f"获取收藏列表失败: {str(e)}")


# -------------------------- 6. 获取用户收藏统计 --------------------------
@favorites_bp.route('/stats', methods=['GET'])
@auth_required
def get_favorite_stats():
    """获取用户收藏统计信息"""
    try:
        count = FavoriteService.get_user_favorite_count(g.user_id)

        return APIResponse.success(
            message='获取成功',
            data={'count': count}
        )

    except Exception as e:
        return APIResponse.server_error(message=f"获取统计失败: {str(e)}")
