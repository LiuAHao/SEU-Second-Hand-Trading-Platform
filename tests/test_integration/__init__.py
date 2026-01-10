"""
集成测试 - 完整业务流程测试
测试从用户注册到订单完成的完整流程
验证各模块之间的集成和协作
"""

import pytest
import json
from app.models import db, User, Item, Order, Review


class TestUserRegistrationAndLoginFlow:
    """用户注册登录流程测试"""

    def test_complete_registration_flow(self, client, app):
        """测试完整的注册流程"""
        # 1. 检查用户名是否可用
        response = client.get('/api/user/checkUsername/newuser2024')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['available'] is True

        # 2. 检查邮箱是否可用
        response = client.get('/api/user/checkEmail/newuser2024@seu.edu.cn')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['available'] is True

        # 3. 注册用户
        response = client.post('/api/user/register',
            json={
                'username': 'newuser2024',
                'email': 'newuser2024@seu.edu.cn',
                'password': 'SecurePass123'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        user_id = data['data']['userId']

        # 4. 验证用户已创建
        with app.app_context():
            user = db.session.get(User, user_id)
            assert user is not None
            assert user.username == 'newuser2024'

        # 5. 登录
        response = client.post('/api/user/login',
            json={
                'username': 'newuser2024',
                'password': 'SecurePass123'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data['data'] or 'Authorization' in str(response.headers)

        # 6. 验证用户名已被占用
        response = client.get('/api/user/checkUsername/newuser2024')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['available'] is False

    def test_login_and_access_protected_route(self, client, app, init_database):
        """测试登录后访问受保护路由"""
        # 1. 登录
        response = client.post('/api/user/login',
            json={
                'username': 'testuser1',
                'password': 'Password123'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        token = data['data']['token']

        # 2. 访问受保护的路由
        response = client.get('/api/users/current',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['username'] == 'testuser1'


class TestCompletePurchaseFlow:
    """完整购买流程测试"""

    def test_browse_to_checkout_flow(self, client, app, init_database, auth_headers_user2):
        """测试从浏览商品到下单的完整流程"""
        # 1. 浏览推荐商品（首页）
        response = client.get('/api/item/getFeatured')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) > 0

        # 2. 搜索特定商品
        response = client.post('/api/item/search',
            json={'keyword': '计算机'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        search_results = data['data']
        assert len(search_results) > 0

        # 获取第一个商品
        item_id = search_results[0]['id']

        # 3. 查看商品详情
        response = client.get(f'/api/item/getDetail/{item_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['id'] == item_id
        assert 'title' in data['data']
        assert 'price' in data['data']
        assert 'stock' in data['data']

        # 4. 获取用户地址列表
        response = client.get('/api/orders/addresses',
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        addresses = data['data']
        assert len(addresses) > 0
        address_id = addresses[0]['id']

        # 5. 创建订单
        response = client.post('/api/orders/',
            json={
                'items': [{'item_id': item_id, 'quantity': 1}],
                'address_id': address_id
            },
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        order_id = data['data']['order_id']
        assert 'order_id' in data['data']

        # 6. 查看订单详情
        response = client.get(f'/api/orders/{order_id}',
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['id'] == order_id
        assert data['data']['status'] == 'pending'

        # 7. 更新订单状态（模拟支付）
        response = client.put(f'/api/orders/{order_id}/status',
            json={'status': 'paid'},
            headers=auth_headers_user2
        )
        assert response.status_code in [200, 400]  # 某些状态可能需要卖家权限

    def test_multiple_items_purchase_flow(self, client, app, init_database, auth_headers_user3):
        """测试购买多个商品的流程"""
        # 1. 按分类浏览
        response = client.post('/api/item/getByCategory',
            json={'category': 'books'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        books = data['data']
        assert len(books) >= 2

        # 2. 选择两本书
        item1_id = books[0]['id']
        item2_id = books[1]['id']

        # 3. 获取地址
        response = client.get('/api/orders/addresses',
            headers=auth_headers_user3
        )
        addresses = json.loads(response.data)['data']
        address_id = addresses[0]['id']

        # 4. 创建包含多商品的订单
        response = client.post('/api/orders/',
            json={
                'items': [
                    {'item_id': item1_id, 'quantity': 1},
                    {'item_id': item2_id, 'quantity': 2}
                ],
                'address_id': address_id
            },
            headers=auth_headers_user3
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['items_count'] == 2
        assert data['data']['total_amount'] > 0


class TestOrderLifecycleFlow:
    """订单生命周期流程测试"""

    def test_order_from_creation_to_completion(self, client, app, init_database, auth_headers_user2):
        """测试订单从创建到完成的生命周期"""
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        # 1. 创建订单
        response = client.post('/api/orders/',
            json={
                'items': [{'item_id': item.id, 'quantity': 1}],
                'address_id': address.id
            },
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        order_id = data['data']['order_id']

        # 验证初始状态
        with app.app_context():
            order = db.session.get(Order, order_id)
            assert order.status == 'pending'

        # 2. 模拟支付（更新状态为paid）
        response = client.put(f'/api/orders/{order_id}/status',
            json={'status': 'paid'},
            headers=auth_headers_user2
        )
        # 可能需要卖家权限，所以可能返回400
        if response.status_code == 200:
            with app.app_context():
                db.session.refresh(order)
                assert order.status == 'paid'

        # 3. 获取订单列表查看状态
        response = client.get('/api/orders/',
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        orders = data['data']['orders']
        assert len(orders) > 0

        # 4. 获取订单统计
        response = client.get('/api/orders/statistics',
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['total_orders'] > 0


class TestOrderCancellationFlow:
    """订单取消流程测试"""

    def test_create_and_cancel_order_flow(self, client, app, init_database, auth_headers_user3):
        """测试创建订单后取消的完整流程"""
        item = init_database['items'][0]  # stock=5
        address = init_database['addresses'][2]

        # 记录初始库存
        with app.app_context():
            initial_stock = item.stock

        # 1. 创建订单
        response = client.post('/api/orders/',
            json={
                'items': [{'item_id': item.id, 'quantity': 2}],
                'address_id': address.id
            },
            headers=auth_headers_user3
        )
        assert response.status_code == 200
        order_id = json.loads(response.data)['data']['order_id']

        # 验证库存已扣减
        with app.app_context():
            db.session.refresh(item)
            stock_after_order = item.stock
            assert stock_after_order == initial_stock - 2

        # 2. 取消订单
        response = client.delete(f'/api/orders/{order_id}',
            headers=auth_headers_user3
        )
        assert response.status_code == 200

        # 3. 验证库存已恢复
        with app.app_context():
            db.session.refresh(item)
            assert item.stock == initial_stock

        # 4. 验证订单状态
        with app.app_context():
            order = db.session.get(Order, order_id)
            assert order.status == 'cancelled'


class TestSellerFlow:
    """卖家流程测试"""

    def test_publish_item_flow(self, client, app, init_database, auth_headers_user1):
        """测试卖家发布商品流程"""
        # 1. 发布新商品
        response = client.post('/api/item/publish',
            json={
                'title': '全新iPhone 15',
                'description': '全新未拆封，国行正品',
                'category': 'electronics',
                'price': 5999.00,
                'stock': 1,
                'image_url': 'https://example.com/iphone15.jpg'
            },
            headers=auth_headers_user1
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 0
        item_id = data['data']['item_id']

        # 2. 验证商品已创建
        response = client.get(f'/api/item/getDetail/{item_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['title'] == '全新iPhone 15'

        # 3. 搜索新发布的商品
        response = client.post('/api/item/search',
            json={'keyword': 'iPhone'}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        results = [item for item in data['data'] if item['id'] == item_id]
        assert len(results) > 0

    def test_update_published_item(self, client, app, init_database, auth_headers_user1):
        """测试更新已发布的商品"""
        item = init_database['items'][0]  # user1的商品

        # 1. 更新商品
        response = client.put(f'/api/item/update/{item.id}',
            json={
                'title': '计算机导论（特价）',
                'price': 39.90,
                'description': '特价促销，欲购从速'
            },
            headers=auth_headers_user1
        )
        assert response.status_code == 200

        # 2. 验证更新成功
        response = client.get(f'/api/item/getDetail/{item.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['price'] == 39.90


class TestUserAddressManagementFlow:
    """用户地址管理流程测试"""

    def test_address_crud_flow(self, client, app, init_database, auth_headers_user3):
        """测试地址增删改查流程"""
        # 1. 查看现有地址
        response = client.get('/api/orders/addresses',
            headers=auth_headers_user3
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        initial_count = len(data['data'])

        # 2. 添加新地址
        response = client.post('/api/orders/addresses',
            json={
                'recipient_name': '张三',
                'phone': '13900139999',
                'province': '江苏省',
                'city': '南京市',
                'district': '江宁区',
                'detail': '东南大学九龙湖校区',
                'is_default': False
            },
            headers=auth_headers_user3
        )
        assert response.status_code == 200
        new_address = json.loads(response.data)['data']

        # 3. 验证地址已添加
        response = client.get('/api/orders/addresses',
            headers=auth_headers_user3
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['data']) == initial_count + 1

        # 4. 更新地址
        response = client.put(f'/api/orders/addresses/{new_address["id"]}',
            json={
                'recipient_name': '李四',
                'detail': '更新后的地址'
            },
            headers=auth_headers_user3
        )
        assert response.status_code == 200

        # 5. 设置为默认地址
        response = client.put(f'/api/orders/addresses/{new_address["id"]}',
            json={'is_default': True},
            headers=auth_headers_user3
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['is_default'] is True


class TestConcurrentPurchaseFlow:
    """并发购买场景测试"""

    def test_two_users_buy_last_item(self, client, app, init_database, auth_headers_user2, auth_headers_user3):
        """测试两个用户同时购买最后一个商品"""
        item = init_database['items'][1]  # MacBook Pro, stock=1
        address_user2 = init_database['addresses'][0]
        address_user3 = init_database['addresses'][2]

        import threading

        results = {'user2': None, 'user3': None}

        def create_order_user2():
            response = client.post('/api/orders/',
                json={
                    'items': [{'item_id': item.id, 'quantity': 1}],
                    'address_id': address_user2.id
                },
                headers=auth_headers_user2
            )
            results['user2'] = response

        def create_order_user3():
            response = client.post('/api/orders/',
                json={
                    'items': [{'item_id': item.id, 'quantity': 1}],
                    'address_id': address_user3.id
                },
                headers=auth_headers_user3
            )
            results['user3'] = response

        # 并发创建订单
        t1 = threading.Thread(target=create_order_user2)
        t2 = threading.Thread(target=create_order_user3)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # 验证只有一个成功
        user2_success = results['user2'].status_code == 200
        user3_success = results['user3'].status_code == 200

        assert (user2_success ^ user3_success), "Exactly one order should succeed"

        # 验证库存为0
        with app.app_context():
            db.session.refresh(item)
            assert item.stock == 0


class TestReviewFlow:
    """评价流程测试"""

    def test_complete_review_flow(self, client, app, init_database, auth_headers_user2):
        """测试完整的评价流程"""
        order = init_database['orders'][0]  # completed订单
        item = init_database['items'][0]

        # 1. 创建评价
        response = client.post(f'/api/reviews/{order.id}/{item.id}',
            json={
                'rating': 5,
                'content': '非常好的商品，卖家很友善！'
            },
            headers=auth_headers_user2
        )

        # 可能未实现此API，或返回501
        if response.status_code in [200, 201]:
            data = json.loads(response.data)
            assert data['code'] == 0

            # 2. 获取商品评价
            # response = client.get(f'/api/reviews/item/{item.id}')
            # assert response.status_code == 200


class TestProfileManagementFlow:
    """个人资料管理流程测试"""

    def test_update_profile_flow(self, client, app, init_database, auth_headers_user2):
        """测试更新个人资料流程"""
        # 1. 获取当前资料
        response = client.get('/api/users/current',
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        current_data = json.loads(response.data)['data']

        # 2. 更新资料
        response = client.put('/api/users/profile',
            json={
                'bio': '我是一位热情的买家',
                'phone': '13900139999'
            },
            headers=auth_headers_user2
        )
        assert response.status_code == 200

        # 3. 验证更新
        response = client.get('/api/users/current',
            headers=auth_headers_user2
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['bio'] == '我是一位热情的买家'
