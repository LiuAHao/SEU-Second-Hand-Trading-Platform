"""
收藏功能业务逻辑服务
处理用户收藏商品的业务逻辑
"""
from app.models import db, Favorite, Item
from sqlalchemy.exc import IntegrityError


class FavoriteService:
    """收藏服务类"""

    @staticmethod
    def add_favorite(user_id, item_id):
        """
        添加收藏
        :param user_id: 用户ID
        :param item_id: 商品ID
        :return: (success, message, favorite)
        """
        try:
            # 检查商品是否存在
            item = Item.query.get(item_id)
            if not item:
                return False, "商品不存在", None

            # 检查是否已收藏
            existing = Favorite.query.filter_by(
                user_id=user_id,
                item_id=item_id
            ).first()

            if existing:
                return False, "已经收藏过该商品", None

            # 创建收藏记录
            favorite = Favorite(user_id=user_id, item_id=item_id)
            db.session.add(favorite)

            # 更新商品收藏计数（触发器应该自动更新，但这里手动更新）
            item.favorites = Favorite.query.filter_by(item_id=item_id).count() + 1

            db.session.commit()

            return True, "收藏成功", favorite

        except Exception as e:
            db.session.rollback()
            return False, f"收藏失败: {str(e)}", None

    @staticmethod
    def remove_favorite(user_id, item_id):
        """
        取消收藏
        :param user_id: 用户ID
        :param item_id: 商品ID
        :return: (success, message)
        """
        try:
            # 查找收藏记录
            favorite = Favorite.query.filter_by(
                user_id=user_id,
                item_id=item_id
            ).first()

            if not favorite:
                return False, "未收藏该商品"

            # 获取商品ID（用于更新计数）
            item_id = favorite.item_id

            # 删除收藏记录
            db.session.delete(favorite)

            # 更新商品收藏计数
            item = Item.query.get(item_id)
            if item:
                item.favorites = Favorite.query.filter_by(item_id=item_id).count()

            db.session.commit()

            return True, "取消收藏成功"

        except Exception as e:
            db.session.rollback()
            return False, f"取消收藏失败: {str(e)}"

    @staticmethod
    def check_favorite(user_id, item_id):
        """
        检查是否已收藏
        :param user_id: 用户ID
        :param item_id: 商品ID
        :return: 是否已收藏
        """
        favorite = Favorite.query.filter_by(
            user_id=user_id,
            item_id=item_id
        ).first()
        return favorite is not None

    @staticmethod
    def get_user_favorites(user_id, page=1, limit=20):
        """
        获取用户的收藏列表
        :param user_id: 用户ID
        :param page: 页码（从1开始）
        :param limit: 每页数量
        :return: (favorites, total)
        """
        try:
            # 分页查询
            pagination = Favorite.query.filter_by(user_id=user_id)\
                .order_by(Favorite.created_at.desc())\
                .paginate(page=page, per_page=limit, error_out=False)

            return pagination.items, pagination.total

        except Exception as e:
            return [], 0

    @staticmethod
    def get_favorite_items(user_id, page=1, limit=20):
        """
        获取用户收藏的商品详情（带分页）
        :param user_id: 用户ID
        :param page: 页码（从1开始）
        :param limit: 每页数量
        :return: (items, total)
        """
        try:
            # 使用JOIN查询收藏的商品
            from sqlalchemy import func

            # 构建查询
            query = db.session.query(
                Item,
                Favorite.created_at.label('favorited_at')
            ).join(
                Favorite, Favorite.item_id == Item.id
            ).filter(
                Favorite.user_id == user_id
            ).order_by(
                Favorite.created_at.desc()
            )

            # 分页
            total = query.count()
            items = query.limit(limit).offset((page - 1) * limit).all()

            # 格式化结果
            result = []
            for item, favorited_at in items:
                item_dict = item.to_dict()
                item_dict['favorited_at'] = favorited_at.isoformat() if favorited_at else None
                result.append(item_dict)

            return result, total

        except Exception as e:
            return [], 0

    @staticmethod
    def toggle_favorite(user_id, item_id):
        """
        切换收藏状态（如果已收藏则取消，未收藏则添加）
        :param user_id: 用户ID
        :param item_id: 商品ID
        :return: (success, message, is_favorited)
        """
        # 检查当前状态
        is_favorited = FavoriteService.check_favorite(user_id, item_id)

        if is_favorited:
            # 已收藏，取消收藏
            success, message = FavoriteService.remove_favorite(user_id, item_id)
            return success, message, False
        else:
            # 未收藏，添加收藏
            success, message, favorite = FavoriteService.add_favorite(user_id, item_id)
            return success, message, True

    @staticmethod
    def get_user_favorite_count(user_id):
        """
        获取用户的收藏总数
        :param user_id: 用户ID
        :return: 收藏数量
        """
        try:
            count = Favorite.query.filter_by(user_id=user_id).count()
            return count
        except Exception as e:
            return 0
