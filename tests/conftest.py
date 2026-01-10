"""
pytest 配置文件
定义测试夹具和全局配置
"""

import pytest
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 在导入 create_app 之前，设置测试环境变量
os.environ['DATABASE_URI'] = 'sqlite:///:memory:'
os.environ['FLASK_ENV'] = 'testing'

from app import create_app, db
from app.models import User, Item, Order, OrderItem, Address, Review
from app.utils.password_helper import PasswordHelper


@pytest.fixture(scope='session')
def app():
    """
    创建应用实例（会话级别）
    用于所有测试
    """
    # 创建应用（使用SQLite内存库）
    app = create_app()
    
    # 配置测试参数
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # 测试中禁用CSRF
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # 创建应用上下文
    with app.app_context():
        # 创建所有数据库表
        db.create_all()
        yield app
        # 测试后清理（可选）
        db.session.remove()


@pytest.fixture(scope='function')
def client(app):
    """
    创建测试客户端（函数级别）
    每个测试函数都会获得新的客户端
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    创建命令行测试运行器
    用于测试CLI命令
    """
    return app.test_cli_runner()


@pytest.fixture
def init_database(app):
    """
    初始化测试数据库
    创建完整的测试数据，包括用户、商品、订单、地址等
    """
    with app.app_context():
        # 清空现有数据（按依赖顺序删除）
        db.session.query(Review).delete()
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.query(Address).delete()
        db.session.query(Item).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # ==================== 创建测试用户（3个） ====================
        test_user1 = User(
            username='testuser1',
            email='testuser1@seu.edu.cn',
            password_hash=PasswordHelper.hash_password('Password123'),
            phone='13800138001',
            avatar_url='https://example.com/avatar1.jpg',
            bio='我是一位诚实的卖家',
            is_active=True
        )
        
        test_user2 = User(
            username='testuser2',
            email='testuser2@seu.edu.cn',
            password_hash=PasswordHelper.hash_password('Password456'),
            phone='13800138002',
            avatar_url='https://example.com/avatar2.jpg',
            bio='我是一位活跃的买家',
            is_active=True
        )
        
        test_user3 = User(
            username='testuser3',
            email='testuser3@seu.edu.cn',
            password_hash=PasswordHelper.hash_password('Password789'),
            phone='13800138003',
            avatar_url='https://example.com/avatar3.jpg',
            bio='我是另一位卖家',
            is_active=True
        )
        
        db.session.add(test_user1)
        db.session.add(test_user2)
        db.session.add(test_user3)
        db.session.commit()
        
        # 创建测试商品
        test_item1 = Item(
            seller_id=test_user1.id,
            title='计算机导论',
            description='2023年新版，全新未使用',
            category='books',
            price=45.50,
            stock=5,
            image_url='https://example.com/item1.jpg',
            is_active=True
        )
        
        test_item2 = Item(
            seller_id=test_user1.id,
            title='MacBook Pro',
            description='2022款，9成新',
            category='electronics',
            price=5999.99,
            stock=1,
            image_url='https://example.com/item2.jpg',
            is_active=True
        )
        
        db.session.add(test_item1)
        db.session.add(test_item2)
        db.session.commit()
        
        # ==================== 创建多个不同分类的商品 ====================
        test_item3 = Item(
            seller_id=test_user3.id,
            title='iPhone 13 Pro',
            description='95新，原装配件齐全',
            category='electronics',
            price=3999.99,
            stock=2,
            image_url='https://example.com/item3.jpg',
            is_active=True
        )
        
        test_item4 = Item(
            seller_id=test_user3.id,
            title='Python编程从入门到精通',
            description='崭新，未阅读',
            category='books',
            price=78.00,
            stock=3,
            image_url='https://example.com/item4.jpg',
            is_active=True
        )
        
        test_item5 = Item(
            seller_id=test_user1.id,
            title='自行车',
            description='捷安特山地车，质量很好',
            category='sports',
            price=899.99,
            stock=1,
            image_url='https://example.com/item5.jpg',
            is_active=True
        )
        
        # 创建一个已下架的商品（用于测试）
        test_item6 = Item(
            seller_id=test_user1.id,
            title='已下架的商品',
            description='此商品已下架',
            category='books',
            price=10.00,
            stock=0,
            image_url='https://example.com/item6.jpg',
            is_active=False
        )
        
        db.session.add_all([test_item3, test_item4, test_item5, test_item6])
        db.session.commit()
        
        # ==================== 创建多个地址 ====================
        test_address1 = Address(
            user_id=test_user2.id,
            recipient_name='张三',
            phone='13800138888',
            detail='九龙湖校区宿舍A1栋202',
            is_default=True
        )
        
        test_address2 = Address(
            user_id=test_user2.id,
            recipient_name='李四',
            phone='13900139000',
            detail='丁香苑宿舍B3栋101',
            is_default=False
        )
        
        test_address3 = Address(
            user_id=test_user1.id,
            recipient_name='王五',
            phone='13700137000',
            detail='四牌楼校区教师宿舍',
            is_default=True
        )
        
        db.session.add_all([test_address1, test_address2, test_address3])
        db.session.commit()
        
        # ==================== 创建测试订单 ====================
        import time
        import random
        
        test_order1 = Order(
            order_number=f'ORD{int(time.time())}{random.randint(1000, 9999)}',
            buyer_id=test_user2.id,
            seller_id=test_user1.id,
            total_amount=91.00,
            status='completed',
            shipping_address='九龙湖校区',
            address_id=test_address1.id,
            total_price=91.00,
            remarks='请放在门口'
        )

        test_order2 = Order(
            order_number=f'ORD{int(time.time())}{random.randint(1000, 9999)}',
            buyer_id=test_user3.id,
            seller_id=test_user1.id,
            total_amount=45.50,
            status='pending',
            shipping_address='丁香苑',
            address_id=test_address2.id,
            total_price=45.50,
            remarks=''
        )
        
        db.session.add_all([test_order1, test_order2])
        db.session.commit()
        
        # ==================== 创建订单明细 ====================
        test_order_item1 = OrderItem(
            order_id=test_order1.id,
            item_id=test_item1.id,
            quantity=2,
            unit_price=45.50
        )
        
        test_order_item2 = OrderItem(
            order_id=test_order2.id,
            item_id=test_item1.id,
            quantity=1,
            unit_price=45.50
        )
        
        db.session.add_all([test_order_item1, test_order_item2])
        db.session.commit()
        
        # ==================== 创建评价 ====================
        test_review = Review(
            order_id=test_order1.id,
            item_id=test_item1.id,
            reviewer_id=test_user2.id,
            reviewee_id=test_user1.id,
            rating=5,
            content='商品很不错，卖家也很友善，五星好评！'
        )
        
        db.session.add(test_review)
        db.session.commit()
        
        # 生成各用户的认证headers
        from app.utils.jwt_helper import generate_token
        token1 = generate_token(user_id=test_user1.id)
        token2 = generate_token(user_id=test_user2.id)
        token3 = generate_token(user_id=test_user3.id)

        # 返回测试数据集合供测试使用
        yield {
            'users': [test_user1, test_user2, test_user3],
            'items': [test_item1, test_item2, test_item3, test_item4, test_item5, test_item6],
            'addresses': [test_address1, test_address2, test_address3],
            'orders': [test_order1, test_order2],
            'order_items': [test_order_item1, test_order_item2],
            'reviews': [test_review],
            'auth_headers_user1': {
                'Authorization': f'Bearer {token1}',
                'Content-Type': 'application/json'
            },
            'auth_headers_user2': {
                'Authorization': f'Bearer {token2}',
                'Content-Type': 'application/json'
            },
            'auth_headers_user3': {
                'Authorization': f'Bearer {token3}',
                'Content-Type': 'application/json'
            }
        }
        
        # 清理数据库
        db.session.query(Review).delete()
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.query(Address).delete()
        db.session.query(Item).delete()
        db.session.query(User).delete()
        db.session.commit()


@pytest.fixture
def auth_headers(app, init_database):
    """
    为第一个测试用户(user1)生成认证header
    """
    from app.utils.jwt_helper import generate_token

    test_user = init_database['users'][0]
    with app.app_context():
        token = generate_token(user_id=test_user.id)

    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def auth_headers_user1(app, init_database):
    """
    为第一个测试用户(user1)生成认证header
    与auth_headers相同，提供更明确的命名
    """
    from app.utils.jwt_helper import generate_token

    test_user = init_database['users'][0]
    with app.app_context():
        token = generate_token(user_id=test_user.id)

    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def auth_headers_user2(app, init_database):
    """
    为第二个测试用户生成认证header
    """
    from app.utils.jwt_helper import generate_token
    
    test_user = init_database['users'][1]
    with app.app_context():
        token = generate_token(user_id=test_user.id)
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def auth_headers_user3(app, init_database):
    """
    为第三个测试用户生成认证header
    """
    from app.utils.jwt_helper import generate_token
    
    test_user = init_database['users'][2]
    with app.app_context():
        token = generate_token(user_id=test_user.id)
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
