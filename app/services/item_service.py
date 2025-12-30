"""
商品业务逻辑服务层
负责处理商品查询、创建、更新、删除等核心业务逻辑
"""
from app.models import Item, User, OrderItem, db
from datetime import datetime
from sqlalchemy import or_, and_

class ItemService:
    """商品服务类"""

    # -------------------------- 1. 获取首页推荐商品 --------------------------
    @staticmethod
    def get_featured_items(limit: int = 12):
        """
        获取首页推荐商品
        :param limit: 返回商品数量
        :return: 业务处理结果
        """
        # 查询推荐商品（按浏览量倒序排序，取前limit条）
        items = Item.query.filter_by(is_active=True).order_by(Item.views.desc()).limit(limit).all()

        # 组装商品数据
        item_list = []
        for item in items:
            seller = User.query.get(item.seller_id)
            item_data = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'price': float(item.price) if item.price else 0.0,
                'stock': item.stock,
                'image': item.image_url or '',
                'category': item.category,
                'seller_id': item.seller_id,
                'seller_name': seller.username if seller else '未知卖家',
                'seller_rating': UserService._get_user_rating(item.seller_id) if seller else 0.0,
                'views': item.views,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
            item_list.append(item_data)

        return {'success': True, 'data': item_list}

    # -------------------------- 2. 搜索商品 --------------------------
    @staticmethod
    def search_items(query: str, search_type: str, page: int = 1, limit: int = 12,
                     category: str = None, min_price: float = None, max_price: float = None,
                     sort: str = 'latest'):
        """
        搜索商品
        :param query: 搜索关键词
        :param search_type: 搜索类型（title/seller/category）
        :param page: 当前页码
        :param limit: 每页数量
        :param category: 分类过滤
        :param min_price: 最小价格
        :param max_price: 最大价格
        :param sort: 排序方式（latest/popular/price-asc/price-desc）
        :return: 业务处理结果
        """
        # 基础查询条件
        query_filter = [Item.is_active == True]

        # 搜索关键词过滤
        if query.strip():
            if search_type == 'title':
                query_filter.append(Item.title.like(f'%{query.strip()}%'))
            elif search_type == 'seller':
                # 关联用户表，按卖家名称搜索
                seller_subquery = User.query.filter(User.username.like(f'%{query.strip()}%')).with_entities(User.id)
                query_filter.append(Item.seller_id.in_(seller_subquery))
            elif search_type == 'category':
                query_filter.append(Item.category.like(f'%{query.strip()}%'))

        # 分类过滤
        if category and category.strip():
            query_filter.append(Item.category == category.strip())

        # 价格过滤
        if min_price is not None and min_price >= 0:
            query_filter.append(Item.price >= min_price)
        if max_price is not None and max_price > 0:
            query_filter.append(Item.price <= max_price)

        # 排序方式
        sort_map = {
            'latest': Item.created_at.desc(),
            'popular': Item.views.desc(),
            'price-asc': Item.price.asc(),
            'price-desc': Item.price.desc()
        }
        order_by = sort_map.get(sort, Item.created_at.desc())

        # 分页查询
        offset = (page - 1) * limit
        items_query = Item.query.filter(and_(*query_filter)).order_by(order_by)
        total_items = items_query.count()
        items = items_query.offset(offset).limit(limit).all()

        # 计算总页数
        total_pages = (total_items + limit - 1) // limit if limit > 0 else 0

        # 组装商品列表
        item_list = []
        for item in items:
            seller = User.query.get(item.seller_id)
            item_data = {
                'id': item.id,
                'title': item.title,
                'description': item.description,
                'price': float(item.price) if item.price else 0.0,
                'stock': item.stock,
                'image': item.image_url or '',
                'category': item.category,
                'seller_id': item.seller_id,
                'seller_name': seller.username if seller else '未知卖家',
                'seller_rating': UserService._get_user_rating(item.seller_id) if seller else 0.0,
                'views': item.views,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
            item_list.append(item_data)

        # 组装分页信息
        pagination = {
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'page_size': limit
        }

        return {
            'success': True,
            'data': {
                'items': item_list,
                'pagination': pagination
            }
        }

    # -------------------------- 3. 按分类获取商品 --------------------------
    @staticmethod
    def get_items_by_category(category: str, page: int = 1, limit: int = 12):
        """
        按分类获取商品
        :param category: 商品分类
        :param page: 当前页码
        :param limit: 每页数量
        :return: 业务处理结果
        """
        # 复用搜索接口逻辑，仅按分类过滤
        return ItemService.search_items(
            query='',
            search_type='title',
            page=page,
            limit=limit,
            category=category,
            sort='latest'
        )

    # -------------------------- 4. 获取商品详情 --------------------------
    @staticmethod
    def get_item_detail(item_id: int):
        """
        获取商品详情
        :param item_id: 商品ID
        :return: 业务处理结果
        """
        item = Item.query.get(item_id)
        if not item or not item.is_active:
            return {'success': False, 'message': '商品不存在或已下架'}

        # 获取卖家信息
        seller = User.query.get(item.seller_id)
        if not seller:
            return {'success': False, 'message': '卖家不存在'}

        # 组装商品详情
        item_detail = {
            'id': item.id,
            'title': item.title,
            'description': item.description,
            'price': float(item.price) if item.price else 0.0,
            'stock': item.stock,
            'image': item.image_url or '',
            'category': item.category,
            'seller_id': item.seller_id,
            'seller_name': seller.username,
            'seller_email': seller.email,
            'seller_rating': UserService._get_user_rating(seller.id),
            'seller_verified': seller.is_active,  # 假设is_active代表是否验证
            'views': item.views,
            'favorites': item.favorites,
            'created_at': item.created_at.isoformat() if item.created_at else None,
            'images': [item.image_url or '']  # 若有多张图片，可扩展为关联表查询
        }

        # 增加商品浏览量
        item.views += 1
        db.session.commit()

        return {'success': True, 'data': item_detail}

    # -------------------------- 5. 发布新商品 --------------------------
    @staticmethod
    def create_item(user_id: int, item_data: dict):
        """
        发布新商品
        :param user_id: 卖家ID
        :param item_data: 商品信息
        :return: 业务处理结果
        """
        # 提取商品字段
        title = item_data.get('title', '').strip()
        description = item_data.get('description', '').strip()
        price = item_data.get('price', 0.0)
        stock = item_data.get('stock', 0)
        category = item_data.get('category', 'other').strip()
        images = item_data.get('images', [])
        image_url = images[0] if images else ''  # 取第一张图片作为主图

        # 字段验证
        if not title:
            return {'success': False, 'message': '商品标题不能为空'}
        if not description:
            return {'success': False, 'message': '商品描述不能为空'}
        if price <= 0:
            return {'success': False, 'message': '商品价格必须大于0'}
        if stock < 0:
            return {'success': False, 'message': '库存数量不能为负数'}

        # 创建商品
        try:
            item = Item(
                seller_id=user_id,
                title=title,
                description=description,
                price=price,
                stock=stock,
                category=category,
                image_url=image_url,
                views=0,
                favorites=0,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(item)
            db.session.commit()

            # 返回商品详情
            return {'success': True, 'data': ItemService.get_item_detail(item.id)['data']}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'发布失败：{str(e)}'}

    # -------------------------- 6. 更新商品 --------------------------
    @staticmethod
    def update_item(item_id: int, user_id: int, item_data: dict):
        """
        更新商品
        :param item_id: 商品ID
        :param user_id: 卖家ID（验证权限）
        :param item_data: 待更新商品信息
        :return: 业务处理结果
        """
        # 查询商品
        item = Item.query.get(item_id)
        if not item:
            return {'success': False, 'message': '商品不存在'}

        # 验证权限（仅卖家可更新自己的商品）
        if item.seller_id != user_id:
            return {'success': False, 'message': '无权限更新该商品'}

        # 更新字段（仅更新传入的非空/有效字段）
        if 'title' in item_data and item_data['title'].strip():
            item.title = item_data['title'].strip()
        if 'description' in item_data and item_data['description'].strip():
            item.description = item_data['description'].strip()
        if 'price' in item_data and item_data['price'] > 0:
            item.price = item_data['price']
        if 'stock' in item_data and item_data['stock'] >= 0:
            item.stock = item_data['stock']
        if 'category' in item_data and item_data['category'].strip():
            item.category = item_data['category'].strip()
        if 'images' in item_data and item_data['images']:
            item.image_url = item_data['images'][0]  # 更新主图

        item.updated_at = datetime.now()

        try:
            db.session.commit()
            # 返回更新后的商品详情
            return {'success': True, 'data': ItemService.get_item_detail(item.id)['data']}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败：{str(e)}'}

    # -------------------------- 7. 删除商品 --------------------------
    @staticmethod
    def delete_item(item_id: int, user_id: int):
        """
        删除商品（逻辑删除，设置is_active=False）
        :param item_id: 商品ID
        :param user_id: 卖家ID（验证权限）
        :return: 业务处理结果
        """
        item = Item.query.get(item_id)
        if not item:
            return {'success': False, 'message': '商品不存在'}

        # 验证权限
        if item.seller_id != user_id:
            return {'success': False, 'message': '无权限删除该商品'}

        # 逻辑删除
        item.is_active = False
        item.updated_at = datetime.now()

        try:
            db.session.commit()
            return {'success': True, 'message': '删除成功'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'删除失败：{str(e)}'}

    # -------------------------- 8. 检查商品库存 --------------------------
    @staticmethod
    def check_stock(item_list: list):
        """
        检查商品库存
        :param item_list: 商品列表 [{'itemId': 1, 'quantity': 2}, ...]
        :return: 业务处理结果
        """
        stock_check_result = []
        is_valid = True

        for item_info in item_list:
            item_id = item_info.get('itemId')
            quantity = item_info.get('quantity', 1)

            # 验证参数
            if not isinstance(item_id, int) or item_id <= 0:
                stock_check_result.append({
                    'itemId': item_id,
                    'available': False,
                    'stock': 0
                })
                is_valid = False
                continue

            if not isinstance(quantity, int) or quantity <= 0:
                stock_check_result.append({
                    'itemId': item_id,
                    'available': False,
                    'stock': 0 if not Item.query.get(item_id) else Item.query.get(item_id).stock
                })
                is_valid = False
                continue

            # 查询商品
            item = Item.query.get(item_id)
            if not item or not item.is_active:
                stock_check_result.append({
                    'itemId': item_id,
                    'available': False,
                    'stock': 0
                })
                is_valid = False
            else:
                available = item.stock >= quantity
                if not available:
                    is_valid = False
                stock_check_result.append({
                    'itemId': item_id,
                    'available': available,
                    'stock': item.stock
                })

        return {
            'success': True,
            'data': {
                'valid': is_valid,
                'items': stock_check_result
            }
        }

# 导入用户服务的内部方法（解决循环导入问题）
from app.services.user_service import UserService