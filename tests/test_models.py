"""
数据模型测试
测试SQLAlchemy模型的各项功能：validation、relationships、methods等
"""

import pytest
from datetime import datetime
from app.models import User, Item, Order, OrderItem, Address, Review, db


class TestUserModel:
    """用户模型测试"""
    
    def test_user_creation(self, app, init_database):
        """测试用户创建"""
        with app.app_context():
            user = User.query.filter_by(username='testuser1').first()
            assert user is not None
            assert user.email == 'testuser1@seu.edu.cn'
            assert user.username == 'testuser1'
            assert user.is_active is True
            assert user.phone == '13800138001'
    
    def test_user_password_hashing(self, app):
        """测试用户密码哈希存储"""
        with app.app_context():
            from app.utils.password_helper import PasswordHelper
            
            user = User(
                username='hashtest',
                email='hashtest@seu.edu.cn',
                password_hash=PasswordHelper.hash_password('TestPass123'),
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            
            retrieved_user = User.query.filter_by(username='hashtest').first()
            assert retrieved_user is not None
            # 密码应该是哈希值，不是明文
            assert retrieved_user.password_hash != 'TestPass123'
            assert len(retrieved_user.password_hash) > 20
    
    def test_user_email_validation_seu_only(self, app):
        """测试邮箱验证器 - 仅接受@seu.edu.cn"""
        with app.app_context():
            # 有效的邮箱
            user_valid = User(
                username='validuser',
                email='validuser@seu.edu.cn',
                password_hash='hash',
                is_active=True
            )
            db.session.add(user_valid)
            db.session.commit()
            assert user_valid.email == 'validuser@seu.edu.cn'
            
            # 无效的邮箱格式
            with pytest.raises(ValueError, match='邮箱必须为东南大学邮箱'):
                user_invalid = User(
                    username='invaliduser',
                    email='invalid@gmail.com',
                    password_hash='hash'
                )
                db.session.add(user_invalid)
                db.session.commit()
    
    def test_user_timestamps(self, app):
        """测试用户的时间戳字段"""
        with app.app_context():
            user = User(
                username='timetest',
                email='timetest@seu.edu.cn',
                password_hash='hash',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            
            # created_at应该被自动设置
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)
            
            # updated_at应该被自动设置
            assert user.updated_at is not None
            assert isinstance(user.updated_at, datetime)
    
    def test_user_relationships(self, app, init_database):
        """测试用户关联关系"""
        with app.app_context():
            seller = User.query.filter_by(username='testuser1').first()
            buyer = User.query.filter_by(username='testuser2').first()
            
            # 卖家发布的商品
            assert len(seller.items) > 0
            assert any(item.title == '计算机导论' for item in seller.items)
            
            # 买家的订单
            assert len(buyer.orders) > 0
            assert buyer.orders[0].buyer_id == buyer.id
            
            # 用户的地址
            assert len(buyer.addresses) > 0
            assert buyer.addresses[0].is_default is True
    
    def test_user_no_duplicate_email(self, app):
        """测试邮箱唯一性约束"""
        with app.app_context():
            # 清除现有数据
            db.session.query(User).delete()
            db.session.commit()
            
            user1 = User(
                username='user1',
                email='duplicate@seu.edu.cn',
                password_hash='hash',
                is_active=True
            )
            db.session.add(user1)
            db.session.commit()
            
            # 尝试创建相同邮箱的用户
            with pytest.raises(Exception):  # IntegrityError
                user2 = User(
                    username='user2',
                    email='duplicate@seu.edu.cn',
                    password_hash='hash',
                    is_active=True
                )
                db.session.add(user2)
                db.session.commit()
    
    def test_user_no_duplicate_username(self, app):
        """测试用户名唯一性约束"""
        with app.app_context():
            # 清除现有数据
            db.session.query(User).delete()
            db.session.commit()
            
            user1 = User(
                username='duplicate',
                email='user1@seu.edu.cn',
                password_hash='hash',
                is_active=True
            )
            db.session.add(user1)
            db.session.commit()
            
            # 尝试创建相同用户名的用户
            with pytest.raises(Exception):  # IntegrityError
                user2 = User(
                    username='duplicate',
                    email='user2@seu.edu.cn',
                    password_hash='hash',
                    is_active=True
                )
                db.session.add(user2)
                db.session.commit()


class TestItemModel:
    """商品模型测试"""
    
    def test_item_creation(self, app, init_database):
        """测试商品创建"""
        with app.app_context():
            item = Item.query.filter_by(title='计算机导论').first()
            assert item is not None
            assert item.price == 45.50
            assert item.stock == 5
            assert item.category == 'books'
            assert item.is_active is True
    
    def test_item_category_validation(self, app, init_database):
        """测试商品分类验证"""
        with app.app_context():
            seller = init_database['users'][0]
            
            # 有效的分类
            valid_categories = ['books', 'electronics', 'sports', 'clothing', 'furniture', 'other']
            
            for category in valid_categories:
                item = Item(
                    seller_id=seller.id,
                    title=f'测试商品-{category}',
                    description='测试',
                    category=category,
                    price=100.0,
                    stock=1
                )
                db.session.add(item)
            
            db.session.commit()
            
            # 检查所有商品都被正确创建
            for category in valid_categories:
                item = Item.query.filter_by(category=category).first()
                assert item is not None
    
    def test_item_invalid_category(self, app, init_database):
        """测试无效分类"""
        with app.app_context():
            seller = init_database['users'][0]
            
            with pytest.raises(ValueError, match='无效分类'):
                item = Item(
                    seller_id=seller.id,
                    title='无效分类商品',
                    description='测试',
                    category='invalid_category',
                    price=100.0,
                    stock=1
                )
                db.session.add(item)
                db.session.commit()
    
    def test_item_price_positive(self, app, init_database):
        """测试商品价格必须为正数"""
        with app.app_context():
            seller = init_database['users'][0]
            
            with pytest.raises(ValueError, match='价格必须大于0'):
                item = Item(
                    seller_id=seller.id,
                    title='负价格商品',
                    description='测试',
                    category='books',
                    price=-10.0,
                    stock=1
                )
                db.session.add(item)
                db.session.commit()
    
    def test_item_stock_non_negative(self, app, init_database):
        """测试商品库存不能为负数"""
        with app.app_context():
            seller = init_database['users'][0]
            
            with pytest.raises(ValueError, match='库存不能为负数'):
                item = Item(
                    seller_id=seller.id,
                    title='负库存商品',
                    description='测试',
                    category='books',
                    price=100.0,
                    stock=-5
                )
                db.session.add(item)
                db.session.commit()
    
    def test_item_timestamps(self, app, init_database):
        """测试商品的时间戳字段"""
        with app.app_context():
            seller = init_database['users'][0]
            item = Item(
                seller_id=seller.id,
                title='时间戳测试',
                description='测试',
                category='books',
                price=50.0,
                stock=1
            )
            db.session.add(item)
            db.session.commit()
            
            assert item.created_at is not None
            assert item.updated_at is not None
    
    def test_item_to_dict(self, app, init_database):
        """测试Item.to_dict()方法"""
        with app.app_context():
            item = Item.query.filter_by(title='计算机导论').first()
            item_dict = item.to_dict()
            
            assert item_dict['id'] == item.id
            assert item_dict['title'] == '计算机导论'
            assert item_dict['price'] == 45.50
            assert item_dict['stock'] == 5
            assert 'category_name' in item_dict
            assert 'seller_name' in item_dict


class TestOrderModel:
    """订单模型测试"""
    
    def test_order_creation(self, app, init_database):
        """测试订单创建"""
        with app.app_context():
            buyer = init_database['users'][1]
            seller = init_database['users'][0]
            
            order = Order(
                buyer_id=buyer.id,
                seller_id=seller.id,
                total_amount=150.50,
                status='pending',
                shipping_address='九龙湖校区'
            )
            db.session.add(order)
            db.session.commit()
            
            retrieved_order = Order.query.filter_by(buyer_id=buyer.id).first()
            assert retrieved_order is not None
            assert retrieved_order.total_amount == 150.50
            assert retrieved_order.status == 'pending'
    
    def test_order_status_validation(self, app, init_database):
        """测试订单状态验证"""
        with app.app_context():
            buyer = init_database['users'][1]
            seller = init_database['users'][0]
            
            # 有效的订单状态
            valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
            
            for idx, status in enumerate(valid_statuses):
                order = Order(
                    buyer_id=buyer.id,
                    seller_id=seller.id,
                    total_amount=100.0,
                    shipping_address='测试地址',
                    status=status
                )
                db.session.add(order)
                db.session.commit()
                
                retrieved = Order.query.filter_by(status=status).first()
                assert retrieved.status == status
    
    def test_order_invalid_status(self, app, init_database):
        """测试无效订单状态"""
        with app.app_context():
            buyer = init_database['users'][1]
            seller = init_database['users'][0]
            
            with pytest.raises(ValueError, match='无效状态'):
                order = Order(
                    buyer_id=buyer.id,
                    seller_id=seller.id,
                    total_amount=100.0,
                    shipping_address='测试地址',
                    status='invalid_status'
                )
                db.session.add(order)
                db.session.commit()
    
    def test_order_timestamps(self, app, init_database):
        """测试订单的时间戳字段"""
        with app.app_context():
            buyer = init_database['users'][1]
            seller = init_database['users'][0]
            
            order = Order(
                buyer_id=buyer.id,
                seller_id=seller.id,
                total_amount=100.0,
                shipping_address='地址',
                status='pending'
            )
            db.session.add(order)
            db.session.commit()
            
            assert order.created_at is not None
            assert order.updated_at is not None


class TestOrderItemModel:
    """订单明细模型测试"""
    
    def test_order_item_creation(self, app, init_database):
        """测试订单明细创建"""
        with app.app_context():
            order = init_database['orders'][0]
            item = init_database['items'][0]
            
            order_item = OrderItem(
                order_id=order.id,
                item_id=item.id,
                quantity=2,
                price_at_purchase=45.50
            )
            db.session.add(order_item)
            db.session.commit()
            
            retrieved_item = OrderItem.query.first()
            assert retrieved_item is not None
            assert retrieved_item.quantity == 2
            assert retrieved_item.price_at_purchase == 45.50
    
    def test_order_item_quantity_positive(self, app, init_database):
        """测试订单明细数量必须为正数"""
        with app.app_context():
            order = init_database['orders'][0]
            item = init_database['items'][0]
            
            with pytest.raises(ValueError, match='数量必须大于0'):
                order_item = OrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    quantity=0,
                    price_at_purchase=50.0
                )
                db.session.add(order_item)
                db.session.commit()


class TestAddressModel:
    """地址模型测试"""
    
    def test_address_creation(self, app, init_database):
        """测试地址创建"""
        with app.app_context():
            user = init_database['users'][1]
            address = Address.query.filter_by(user_id=user.id).first()
            
            assert address is not None
            assert address.recipient_name == '张三'
            assert address.detail == '九龙湖校区宿舍A1栋202'
            assert address.is_default is True
    
    def test_address_multiple(self, app, init_database):
        """测试用户多地址"""
        with app.app_context():
            user = init_database['users'][1]
            
            # 应该有多个地址
            user_addresses = Address.query.filter_by(user_id=user.id).all()
            assert len(user_addresses) >= 2
    
    def test_address_default_flag(self, app, init_database):
        """测试地址默认标记"""
        with app.app_context():
            user = init_database['users'][1]
            
            # 应该有一个默认地址
            default_addresses = Address.query.filter_by(
                user_id=user.id,
                is_default=True
            ).all()
            assert len(default_addresses) >= 1
            
            # 应该有非默认地址
            non_default = Address.query.filter_by(
                user_id=user.id,
                is_default=False
            ).all()
            assert len(non_default) >= 1


class TestReviewModel:
    """评价模型测试"""
    
    def test_review_creation(self, app, init_database):
        """测试评价创建"""
        with app.app_context():
            reviewer = init_database['users'][1]
            reviewee = init_database['users'][0]
            item = init_database['items'][0]
            order = init_database['orders'][0]
            
            review = Review(
                order_id=order.id,
                item_id=item.id,
                reviewer_id=reviewer.id,
                reviewee_id=reviewee.id,
                rating=5,
                content='很满意，五星好评！'
            )
            db.session.add(review)
            db.session.commit()
            
            retrieved_review = Review.query.first()
            assert retrieved_review is not None
            assert retrieved_review.rating == 5
            assert retrieved_review.content == '很满意，五星好评！'
    
    def test_review_rating_range(self, app, init_database):
        """测试评分范围（1-5）"""
        with app.app_context():
            reviewer = init_database['users'][1]
            reviewee = init_database['users'][0]
            item = init_database['items'][1]
            buyer = init_database['users'][1]
            seller = init_database['users'][0]
            
            # 创建新订单用于评价
            order = Order(
                buyer_id=buyer.id,
                seller_id=seller.id,
                total_amount=100.0,
                shipping_address='测试',
                status='completed'
            )
            db.session.add(order)
            db.session.commit()
            
            # 测试各个有效的评分
            for rating in [1, 2, 3, 4, 5]:
                review = Review(
                    order_id=order.id,
                    item_id=item.id,
                    reviewer_id=reviewer.id,
                    reviewee_id=reviewee.id,
                    rating=rating,
                    content=f'{rating}星评价'
                )
                db.session.add(review)
                db.session.commit()
                
                retrieved = Review.query.filter_by(rating=rating).first()
                assert retrieved.rating == rating
    
    def test_review_invalid_rating(self, app, init_database):
        """测试无效评分"""
        with app.app_context():
            reviewer = init_database['users'][1]
            reviewee = init_database['users'][0]
            item = init_database['items'][0]
            order = init_database['orders'][0]
            
            # 评分超出范围
            with pytest.raises(ValueError, match='评分必须在1-5之间'):
                review = Review(
                    order_id=order.id,
                    item_id=item.id,
                    reviewer_id=reviewer.id,
                    reviewee_id=reviewee.id,
                    rating=10,
                    content='超出范围'
                )
                db.session.add(review)
                db.session.commit()


class TestDatabaseIntegrity:
    """数据库完整性测试"""
    
    def test_cascade_delete_items(self, app, init_database):
        """测试级联删除 - 删除用户时其商品也被删除"""
        with app.app_context():
            user = User.query.filter_by(username='testuser3').first()
            user_id = user.id
            
            # 获取用户商品数量
            item_count_before = len(user.items)
            assert item_count_before > 0
            
            # 删除用户
            db.session.delete(user)
            db.session.commit()
            
            # 检查用户是否被删除
            user_exists = User.query.filter_by(id=user_id).first()
            assert user_exists is None
            
            # 检查用户的商品是否被级联删除
            items_exist = Item.query.filter_by(seller_id=user_id).all()
            assert len(items_exist) == 0
    
    def test_cascade_delete_orders(self, app, init_database):
        """测试级联删除 - 删除订单时其明细也被删除"""
        with app.app_context():
            order = init_database['orders'][0]
            order_id = order.id
            
            # 获取订单明细数量
            item_count = len(order.order_items)
            assert item_count > 0
            
            # 删除订单
            db.session.delete(order)
            db.session.commit()
            
            # 检查订单明细是否被级联删除
            items_exist = OrderItem.query.filter_by(order_id=order_id).all()
            assert len(items_exist) == 0
    
    def test_foreign_key_constraint_seller(self, app):
        """测试外键约束 - 商品的卖家必须存在"""
        with app.app_context():
            # 尝试创建指向不存在用户的商品
            with pytest.raises(Exception):  # IntegrityError
                item = Item(
                    seller_id=99999,
                    title='违反约束的商品',
                    description='测试',
                    category='books',
                    price=100.0,
                    stock=1
                )
                db.session.add(item)
                db.session.commit()
    
    def test_foreign_key_constraint_order_buyer(self, app):
        """测试外键约束 - 订单的买家必须存在"""
        with app.app_context():
            with pytest.raises(Exception):  # IntegrityError
                order = Order(
                    buyer_id=99999,
                    seller_id=99998,
                    total_amount=100.0,
                    shipping_address='地址',
                    status='pending'
                )
                db.session.add(order)
                db.session.commit()
    
    def test_foreign_key_constraint(self, app):
        """测试外键约束"""
        with app.app_context():
            # 尝试创建指向不存在用户的商品
            with pytest.raises(Exception):  # SQLAlchemy会抛出IntegrityError
                item = Item(
                    seller_id=99999,  # 不存在的用户ID
                    title='违反约束的商品',
                    description='测试',
                    category='books',
                    price=100.0,
                    stock=1
                )
                db.session.add(item)
                db.session.commit()