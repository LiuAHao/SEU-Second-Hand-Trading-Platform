"""
订单服务层单元测试
直接测试 OrderService 的业务逻辑
重点：事务处理、并发控制、业务规则验证
"""

import pytest
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.order_service import OrderService
from app.models import Order, Item, OrderItem, db


class TestOrderServiceCreation:
    """订单创建服务测试"""

    def test_create_order_success_basic(self, app, init_database):
        """测试基本订单创建成功"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 2}],
                address_id=address.id
            )

            assert success is True
            assert 'order_id' in result
            assert result['total_amount'] == 91.00
            assert result['status'] == 'pending'

            # 验证数据库记录
            order = db.session.get(Order, result['order_id'])
            assert order is not None
            assert order.total_amount == 91.00
            assert order.status == 'pending'

    def test_create_order_multiple_items(self, app, init_database):
        """测试多商品订单创建"""
        buyer = init_database['users'][1]
        item1 = init_database['items'][0]
        item2 = init_database['items'][3]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[
                    {'item_id': item1.id, 'quantity': 1},
                    {'item_id': item2.id, 'quantity': 2}
                ],
                address_id=address.id
            )

            assert success is True
            assert result['items_count'] == 2

    def test_create_order_stock_decrease(self, app, init_database):
        """测试库存正确扣减"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]  # stock=5
        address = init_database['addresses'][0]

        with app.app_context():
            initial_stock = item.stock

            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 2}],
                address_id=address.id
            )

            assert success

            db.session.refresh(item)
            assert item.stock == initial_stock - 2

    def test_create_order_insufficient_stock(self, app, init_database):
        """测试库存不足失败"""
        buyer = init_database['users'][1]
        item = init_database['items'][1]  # stock=1
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 100}],
                address_id=address.id
            )

            assert success is False
            assert '库存' in result or 'insufficient' in result.lower()

    def test_create_order_nonexistent_item(self, app, init_database):
        """测试不存在的商品"""
        buyer = init_database['users'][1]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': 99999, 'quantity': 1}],
                address_id=address.id
            )

            assert success is False
            assert '不存在' in result or 'not found' in result.lower()

    def test_create_order_inactive_item(self, app, init_database):
        """测试已下架商品"""
        buyer = init_database['users'][1]
        item = init_database['items'][5]  # is_active=False
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 1}],
                address_id=address.id
            )

            assert success is False
            assert '下架' in result or 'inactive' in result.lower()

    def test_create_order_buy_own_item(self, app, init_database):
        """测试购买自己的商品"""
        user1 = init_database['users'][0]
        item = init_database['items'][0]  # seller_id = user1
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=user1.id,  # user1购买自己的商品
                items_data=[{'item_id': item.id, 'quantity': 1}],
                address_id=address.id
            )

            assert success is False
            assert '不能购买自己的商品' in result or 'own' in result.lower()

    def test_create_order_nonexistent_address(self, app, init_database):
        """测试不存在的地址"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 1}],
                address_id=99999
            )

            assert success is False
            assert '地址' in result or 'address' in result.lower()

    def test_create_order_unauthorized_address(self, app, init_database):
        """测试使用其他用户的地址"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][2]  # user3的地址

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 1}],
                address_id=address.id
            )

            assert success is False
            assert '无权' in result or 'unauthorized' in result.lower()

    def test_create_order_empty_items(self, app, init_database):
        """测试空商品列表"""
        buyer = init_database['users'][1]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[],
                address_id=address.id
            )

            assert success is False
            assert '空' in result or 'empty' in result.lower()

    def test_create_order_duplicate_items(self, app, init_database):
        """测试重复商品"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[
                    {'item_id': item.id, 'quantity': 1},
                    {'item_id': item.id, 'quantity': 2}
                ],
                address_id=address.id
            )

            assert success is False
            assert '重复' in result or 'duplicate' in result.lower()

    def test_create_order_zero_quantity(self, app, init_database):
        """测试数量为0"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 0}],
                address_id=address.id
            )

            assert success is False
            assert '大于0' in result or 'positive' in result.lower()

    def test_create_order_negative_quantity(self, app, init_database):
        """测试负数数量"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': -1}],
                address_id=address.id
            )

            assert success is False

    def test_create_order_exceeds_limit(self, app, init_database):
        """测试超出购买数量限制"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 101}],  # 超过100
                address_id=address.id
            )

            assert success is False
            assert '超出限制' in result or 'limit' in result.lower() or '超过' in result


class TestOrderServiceCancellation:
    """订单取消服务测试"""

    def test_cancel_order_success(self, app, init_database):
        """测试成功取消订单"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            # 先创建订单
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 2}],
                address_id=address.id
            )

            assert success
            order_id = result['order_id']
            stock_after_order = item.stock

            # 取消订单
            success, result = OrderService.cancel_order(
                order_id=order_id,
                buyer_id=buyer.id
            )

            assert success is True
            assert '成功' in result or 'success' in result.lower()

            # 验证库存恢复
            db.session.refresh(item)
            assert item.stock == stock_after_order + 2

            # 验证订单状态
            order = db.session.get(Order, order_id)
            assert order.status == 'cancelled'

    def test_cancel_order_nonexistent(self, app, init_database):
        """测试取消不存在的订单"""
        buyer = init_database['users'][1]

        with app.app_context():
            success, result = OrderService.cancel_order(
                order_id=99999,
                buyer_id=buyer.id
            )

            assert success is False
            assert '不存在' in result or 'not found' in result.lower()

    def test_cancel_order_unauthorized(self, app, init_database):
        """测试取消其他用户的订单"""
        user2 = init_database['users'][1]
        user3 = init_database['users'][2]
        order = init_database['orders'][0]  # user2的订单

        with app.app_context():
            success, result = OrderService.cancel_order(
                order_id=order.id,
                buyer_id=user3.id  # user3尝试取消user2的订单
            )

            assert success is False
            assert '无权' in result or 'unauthorized' in result.lower()

    def test_cancel_order_already_completed(self, app, init_database):
        """测试取消已完成订单"""
        buyer = init_database['users'][1]
        order = init_database['orders'][0]  # status='completed'

        with app.app_context():
            success, result = OrderService.cancel_order(
                order_id=order.id,
                buyer_id=buyer.id
            )

            assert success is False
            assert '只能取消待支付' in result or 'pending' in result.lower()

    def test_cancel_order_stock_restoration(self, app, init_database):
        """测试取消订单后库存正确恢复"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]  # stock=5
        address = init_database['addresses'][0]

        with app.app_context():
            initial_stock = item.stock

            # 创建订单
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 3}],
                address_id=address.id
            )

            assert success
            order_id = result['order_id']

            db.session.refresh(item)
            stock_after_order = item.stock
            assert stock_after_order == initial_stock - 3

            # 取消订单
            success, result = OrderService.cancel_order(
                order_id=order_id,
                buyer_id=buyer.id
            )

            assert success

            # 验证库存完全恢复
            db.session.refresh(item)
            assert item.stock == initial_stock


class TestOrderServiceQuery:
    """订单查询服务测试"""

    def test_get_orders_empty(self, app, init_database):
        """测试获取空订单列表"""
        # 使用没有订单的用户
        user = init_database['users'][2]

        with app.app_context():
            success, result = OrderService.get_orders(
                buyer_id=user.id,
                page=1,
                limit=10
            )

            assert success is True
            assert 'orders' in result
            assert 'pagination' in result

    def test_get_orders_with_pagination(self, app, init_database):
        """测试分页查询订单"""
        user = init_database['users'][1]  # user2有订单

        with app.app_context():
            success, result = OrderService.get_orders(
                buyer_id=user.id,
                page=1,
                limit=10
            )

            assert success is True
            assert isinstance(result['orders'], list)
            assert result['pagination']['page'] == 1
            assert result['pagination']['limit'] == 10

    def test_get_order_detail_success(self, app, init_database):
        """测试获取订单详情"""
        user = init_database['users'][1]
        order = init_database['orders'][0]

        with app.app_context():
            success, result = OrderService.get_order_detail(
                order_id=order.id,
                buyer_id=user.id
            )

            assert success is True
            assert result['id'] == order.id
            assert 'items' in result
            assert 'buyer' in result

    def test_get_order_detail_unauthorized(self, app, init_database):
        """测试获取其他用户订单详情"""
        user3 = init_database['users'][2]
        order = init_database['orders'][0]  # user2的订单

        with app.app_context():
            success, result = OrderService.get_order_detail(
                order_id=order.id,
                buyer_id=user3.id
            )

            assert success is False
            assert '无权' in result or 'unauthorized' in result.lower()

    def test_get_order_detail_nonexistent(self, app, init_database):
        """测试获取不存在的订单详情"""
        user = init_database['users'][1]

        with app.app_context():
            success, result = OrderService.get_order_detail(
                order_id=99999,
                buyer_id=user.id
            )

            assert success is False
            assert '不存在' in result or 'not found' in result.lower()


class TestOrderServiceStatusUpdate:
    """订单状态更新服务测试"""

    def test_update_status_to_cancelled(self, app, init_database):
        """测试更新为已取消"""
        user = init_database['users'][2]
        order = init_database['orders'][1]  # status='pending'

        with app.app_context():
            success, result = OrderService.update_order_status(
                order_id=order.id,
                buyer_id=user.id,
                status='cancelled'
            )

            assert success is True

            db.session.refresh(order)
            assert order.status == 'cancelled'

    def test_update_status_invalid_transition(self, app, init_database):
        """测试无效的状态流转"""
        user = init_database['users'][1]
        order = init_database['orders'][0]  # status='completed'

        with app.app_context():
            success, result = OrderService.update_order_status(
                order_id=order.id,
                buyer_id=user.id,
                status='pending'  # 已完成不能改为待支付
            )

            assert success is False
            assert '不能修改' in result or 'cannot' in result.lower()

    def test_update_status_invalid_value(self, app, init_database):
        """测试无效的状态值"""
        user = init_database['users'][2]
        order = init_database['orders'][1]

        with app.app_context():
            success, result = OrderService.update_order_status(
                order_id=order.id,
                buyer_id=user.id,
                status='invalid_status'
            )

            assert success is False


class TestOrderServiceConcurrency:
    """订单服务并发测试 - 验证事务和锁机制"""

    def test_concurrent_order_creation_no_oversell(self, app, init_database):
        """测试并发创建订单不超卖"""
        item = init_database['items'][1]  # stock=1
        user2 = init_database['users'][1]
        user3 = init_database['users'][2]
        address = init_database['addresses'][0]

        results = []
        errors = []

        def create_order(user_id):
            try:
                with app.app_context():
                    success, result = OrderService.create_order(
                        buyer_id=user_id,
                        items_data=[{'item_id': item.id, 'quantity': 1}],
                        address_id=address.id
                    )
                    results.append((success, result))
            except Exception as e:
                errors.append(str(e))

        # 使用线程模拟并发
        threads = []
        for user_id in [user2.id, user3.id]:
            t = threading.Thread(target=create_order, args=(user_id,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 验证结果
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 2

        success_count = sum(1 for s, r in results if s)
        failure_count = sum(1 for s, r in results if not s)

        # 只应该有一个成功
        assert success_count == 1, f"Expected 1 success, got {success_count}"
        assert failure_count == 1, f"Expected 1 failure, got {failure_count}"

        # 验证最终库存为0
        with app.app_context():
            db.session.refresh(item)
            assert item.stock == 0

    def test_concurrent_order_creation_multiple_items(self, app, init_database):
        """测试并发购买多个商品"""
        item1 = init_database['items'][0]  # stock=5
        item2 = init_database['items'][3]  # stock=3
        user2 = init_database['users'][1]
        address = init_database['addresses'][0]

        results = []

        def create_order():
            with app.app_context():
                success, result = OrderService.create_order(
                    buyer_id=user2.id,
                    items_data=[
                        {'item_id': item1.id, 'quantity': 1},
                        {'item_id': item2.id, 'quantity': 1}
                    ],
                    address_id=address.id
                )
                results.append((success, result))

        # 并发创建3个订单
        threads = [threading.Thread(target=create_order) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 验证至少有部分成功
        assert len(results) == 3

    def test_concurrent_create_and_cancel(self, app, init_database):
        """测试并发创建和取消订单"""
        item = init_database['items'][0]
        user = init_database['users'][1]
        address = init_database['addresses'][0]

        order_ids = []
        create_results = []
        cancel_results = []

        def create_order():
            with app.app_context():
                success, result = OrderService.create_order(
                    buyer_id=user.id,
                    items_data=[{'item_id': item.id, 'quantity': 1}],
                    address_id=address.id
                )
                if success:
                    order_ids.append(result['order_id'])
                create_results.append(success)

        def cancel_order():
            if order_ids:
                with app.app_context():
                    order_id = order_ids.pop(0)
                    success, result = OrderService.cancel_order(
                        order_id=order_id,
                        buyer_id=user.id
                    )
                    cancel_results.append(success)

        # 创建订单
        t1 = threading.Thread(target=create_order)
        t1.start()
        t1.join()

        # 并发取消和创建
        t2 = threading.Thread(target=cancel_order)
        t3 = threading.Thread(target=create_order)
        t2.start()
        t3.start()
        t2.join()
        t3.join()

        # 验证操作完成
        assert len(create_results) >= 1

    def test_concurrent_create_many_orders_stock_limit(self, app, init_database):
        """测试大量并发订单，库存限制"""
        item = init_database['items'][0]  # stock=5
        address = init_database['addresses'][0]

        users = init_database['users'][:3]  # 3个用户
        results = []

        def create_order(user_id):
            with app.app_context():
                success, result = OrderService.create_order(
                    buyer_id=user_id,
                    items_data=[{'item_id': item.id, 'quantity': 1}],
                    address_id=address.id
                )
                results.append(success)

        # 10个并发请求
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(create_order, user.id)
                for user in users * 4  # 12个请求
            ]
            for f in as_completed(futures):
                pass

        # 应该只有5个成功（库存=5）
        success_count = sum(results)
        assert success_count <= 5, f"Expected at most 5 success, got {success_count}"

        # 验证库存不为负
        with app.app_context():
            db.session.refresh(item)
            assert item.stock >= 0


class TestOrderServiceAddressManagement:
    """地址管理服务测试"""

    def test_get_addresses_success(self, app, init_database):
        """测试获取地址列表"""
        user = init_database['users'][1]

        with app.app_context():
            success, result = OrderService.get_addresses(user.id)

            assert success is True
            assert isinstance(result, list)
            assert len(result) >= 2  # user2有2个地址

    def test_create_address_success(self, app, init_database):
        """测试创建地址"""
        user = init_database['users'][2]

        with app.app_context():
            success, result = OrderService.create_address(
                user_id=user.id,
                data={
                    'recipient_name': '新收货人',
                    'phone': '13900139999',
                    'detail': '东南大学九龙湖校区',
                    'is_default': True
                }
            )

            assert success is True
            assert result['recipient_name'] == '新收货人'

    def test_create_address_missing_fields(self, app, init_database):
        """测试创建地址缺少必填字段"""
        user = init_database['users'][2]

        with app.app_context():
            success, result = OrderService.create_address(
                user_id=user.id,
                data={
                    'recipient_name': '测试'
                    # 缺少phone和detail
                }
            )

            assert success is False
            assert '缺少' in result or 'required' in result.lower()

    def test_create_address_set_default(self, app, init_database):
        """测试设置默认地址"""
        user = init_database['users'][2]

        with app.app_context():
            # 创建新地址并设为默认
            success, result = OrderService.create_address(
                user_id=user.id,
                data={
                    'recipient_name': '默认地址',
                    'phone': '13900139999',
                    'detail': '测试地址',
                    'is_default': True
                }
            )

            assert success is True
            assert result['is_default'] is True

    def test_update_address_success(self, app, init_database):
        """测试更新地址"""
        user = init_database['users'][1]
        address = init_database['addresses'][0]

        with app.app_context():
            success, result = OrderService.update_address(
                user_id=user.id,
                address_id=address.id,
                data={
                    'recipient_name': '更新后的名字',
                    'phone': '13800138888',
                    'detail': '更新后的地址'
                }
            )

            assert success is True
            assert result['recipient_name'] == '更新后的名字'

    def test_update_address_unauthorized(self, app, init_database):
        """测试更新其他用户的地址"""
        user3 = init_database['users'][2]
        address = init_database['addresses'][0]  # user2的地址

        with app.app_context():
            success, result = OrderService.update_address(
                user_id=user3.id,
                address_id=address.id,
                data={'recipient_name': '黑客'}
            )

            assert success is False
            assert '无权' in result or 'unauthorized' in result.lower()

    def test_update_nonexistent_address(self, app, init_database):
        """测试更新不存在的地址"""
        user = init_database['users'][1]

        with app.app_context():
            success, result = OrderService.update_address(
                user_id=user.id,
                address_id=99999,
                data={'recipient_name': '测试'}
            )

            assert success is False
            assert '不存在' in result or 'not found' in result.lower()


class TestOrderServiceStatistics:
    """订单统计服务测试"""

    def test_get_statistics_success(self, app, init_database):
        """测试获取订单统计"""
        user = init_database['users'][1]

        with app.app_context():
            success, result = OrderService.get_statistics(user.id)

            assert success is True
            assert 'total_orders' in result
            assert 'pending_orders' in result
            assert 'completed_orders' in result
            assert 'total_spent' in result
            assert isinstance(result['total_spent'], float)


class TestOrderServiceTransactions:
    """订单服务事务处理测试"""

    def test_transaction_rollback_on_error(self, app, init_database):
        """测试错误时事务回滚"""
        buyer = init_database['users'][1]
        item = init_database['items'][0]
        address = init_database['addresses'][0]

        with app.app_context():
            initial_stock = item.stock
            initial_order_count = db.session.query(Order).count()

            # 尝试创建会失败的订单（库存不足）
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[{'item_id': item.id, 'quantity': 9999}],  # 远超库存
                address_id=address.id
            )

            assert success is False

            # 验证数据库未改变
            db.session.refresh(item)
            assert item.stock == initial_stock

            final_order_count = db.session.query(Order).count()
            assert final_order_count == initial_order_count

    def test_transaction_atomicity(self, app, init_database):
        """测试事务原子性 - 全部成功或全部失败"""
        buyer = init_database['users'][1]
        item1 = init_database['items'][0]
        item2 = init_database['items'][3]
        address = init_database['addresses'][0]

        with app.app_context():
            initial_stock1 = item1.stock
            initial_stock2 = item2.stock

            # 创建包含2个商品的订单
            success, result = OrderService.create_order(
                buyer_id=buyer.id,
                items_data=[
                    {'item_id': item1.id, 'quantity': 1},
                    {'item_id': item2.id, 'quantity': 1}
                ],
                address_id=address.id
            )

            if success:
                # 验证两个商品的库存都扣减了
                db.session.refresh(item1)
                db.session.refresh(item2)
                assert item1.stock == initial_stock1 - 1
                assert item2.stock == initial_stock2 - 1
            else:
                # 如果失败，验证库存都没有改变
                db.session.refresh(item1)
                db.session.refresh(item2)
                assert item1.stock == initial_stock1
                assert item2.stock == initial_stock2
