"""
订单业务逻辑服务
处理订单相关的业务逻辑：创建、查询、取消等
关键：事务处理、库存管理、并发控制

这是整个后端最复杂的模块，需要特别关注：
- 数据库事务处理 (BEGIN/COMMIT/ROLLBACK)
- 行级锁 (SELECT FOR UPDATE) 防止库存冲突
- 原子性操作保证
"""

from app.models import db, Order, OrderItem, Item, Address, User
from app.utils.response import error_response, success_response
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload, selectinload
from decimal import Decimal
from datetime import datetime
import traceback
import logging
import time
import random

logger = logging.getLogger(__name__)


class OrderService:
    """订单服务类"""
    
    @staticmethod
    def create_order(buyer_id, items_data, address_id):
        """
        创建订单 - 最复杂的操作！
        完整事务流程：
        1. 开启事务
        2. 检查地址是否存在
        3. 对每个商品：锁定库存行 + 检查库存
        4. 计算总金额
        5. 扣减库存
        6. 创建订单记录
        7. 创建订单明细
        8. 提交或回滚
        
        Args:
            buyer_id: 买家ID
            items_data: [
                {'item_id': 1, 'quantity': 2},
                {'item_id': 2, 'quantity': 1}
            ]
            address_id: 配送地址ID
            
        Returns:
            (success, result_or_error_message)
        """
        # 验证输入数据
        if not items_data:
            return False, "购物车为空"
        
        if not isinstance(items_data, list):
            return False, "items_data必须是列表"
        
        # 检查是否有重复的商品ID
        item_ids = [item['item_id'] for item in items_data]
        if len(item_ids) != len(set(item_ids)):
            return False, "购物车中存在重复商品"
        
        # 开启事务
        try:
            # 使用SQLAlchemy的会话进行事务管理
            session = db.session
            
            # ==================== 步骤1: 检查地址是否存在 ====================
            address = session.get(Address, address_id)
            if not address:
                return False, "配送地址不存在"
            
            if address.user_id != buyer_id:
                return False, "无权使用该配送地址"
            
            # ==================== 步骤2: 获取所有商品并锁定库存 ====================
            # 为了性能，先查询所有商品
            stmt = select(Item).where(Item.id.in_(item_ids)).with_for_update()
            items_result = session.execute(stmt)
            all_items = {item.id: item for item in items_result.scalars().all()}
            
            # 检查商品是否存在且可用
            missing_items = []
            inactive_items = []
            for item_data in items_data:
                item_id = item_data['item_id']
                quantity = item_data['quantity']
                
                if item_id not in all_items:
                    missing_items.append(item_id)
                    continue
                    
                item = all_items[item_id]
                
                # 检查商品是否在售
                if not item.is_active:
                    inactive_items.append(item_id)
                    continue
                
                # 检查库存是否充足（此时item已被锁定）
                if item.stock < quantity:
                    return False, f"商品 {item.title} 库存不足，剩余 {item.stock} 件"
                
                # 检查是否购买自己的商品
                if item.seller_id == buyer_id:
                    return False, f"不能购买自己的商品: {item.title}"
                
                # 验证数量
                if quantity <= 0:
                    return False, f"商品 {item.title} 购买数量必须大于0"
                if quantity > 100:  # 防止异常大量购买
                    return False, f"商品 {item.title} 购买数量超出限制"
            
            if missing_items:
                return False, f"商品不存在: {missing_items}"
            if inactive_items:
                return False, f"商品已下架: {inactive_items}"
            
            # ==================== 步骤3: 计算总金额 ====================
            total_amount = Decimal('0.00')
            order_items_data = []
            
            for item_data in items_data:
                item_id = item_data['item_id']
                quantity = item_data['quantity']
                item = all_items[item_id]
                
                # 计算金额（数量 * 单价）
                item_total = Decimal(str(item.price)) * Decimal(str(quantity))
                total_amount += item_total
                
                # 准备订单明细数据
                order_items_data.append({
                    'item': item,
                    'quantity': quantity,
                    'unit_price': item.price,
                    'item_total': item_total
                })
            
            # 检查总金额是否合理
            if total_amount <= Decimal('0.00'):
                return False, "订单总金额必须大于0"
            
            # ==================== 步骤4: 创建订单记录 ====================
            shipping_address = f"{address.recipient_name} {address.phone} {address.detail}"
            if address.city:
                shipping_address = f"{address.city}{address.district or ''}{address.detail}"

            # 生成订单号：ORD + 时间戳 + 随机数
            timestamp = int(time.time())
            random_num = random.randint(1000, 9999)
            order_number = f"ORD{timestamp}{random_num}"

            # 获取卖家ID（从第一个商品）
            first_item = all_items[items_data[0]['item_id']]
            seller_id = first_item.seller_id
            
            order = Order(
                order_number=order_number,  # 添加订单号
                buyer_id=buyer_id,
                total_amount=total_amount,
                seller_id=seller_id,  # 从第一个商品获取卖家ID
                address_id=address_id,  # 添加地址ID
                status='pending',
                shipping_address=shipping_address,
                total_price=total_amount,  # 设置total_price（与total_amount相同）
                remarks='',  # 空备注
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(order)
            
            # 立即flush，获取order.id（但不提交事务）
            session.flush()
            
            # ==================== 步骤5: 创建订单明细并扣减库存 ====================
            for item_data in order_items_data:
                item = item_data['item']
                quantity = item_data['quantity']
                
                # 创建订单明细
                order_item = OrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    quantity=quantity,
                    unit_price=item.price,
                    created_at=datetime.now()
                )
                session.add(order_item)
                
                # 扣减库存
                item.stock -= quantity
                item.updated_at = datetime.now()
                
                # 记录库存变化日志
                logger.info(f"订单 {order.id}: 商品 {item.id} 扣减库存 {quantity}, 剩余 {item.stock}")
            
            # ==================== 步骤6: 提交事务 ====================
            session.commit()
            
            logger.info(f"订单创建成功: 订单ID={order.id}, 买家ID={buyer_id}, 总金额={total_amount}")
            
            # 返回订单信息
            order_info = {
                'order_id': order.id,
                'total_amount': float(total_amount),
                'status': order.status,
                'shipping_address': order.shipping_address,
                'created_at': order.created_at.isoformat(),
                'items_count': len(order_items_data)
            }
            
            return True, order_info
            
        except Exception as e:
            # 发生异常时回滚事务
            db.session.rollback()
            logger.error(f"创建订单失败: {str(e)}\n{traceback.format_exc()}")
            
            # 返回具体的错误信息
            error_msg = str(e)
            if "stock" in error_msg.lower() or "库存" in error_msg:
                return False, "库存不足，请刷新页面后重试"
            elif "foreign key" in error_msg.lower():
                return False, "数据验证失败，请检查商品或地址信息"
            else:
                return False, f"创建订单失败: {error_msg}"
    
    @staticmethod
    def get_orders(buyer_id, page=1, limit=10):
        """获取用户订单列表"""
        try:
            session = db.session
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询订单总数
            total = session.query(Order).filter(
                Order.buyer_id == buyer_id
            ).count()
            
            # 查询订单列表（按创建时间倒序）
            orders = session.query(Order).filter(
                Order.buyer_id == buyer_id
            ).order_by(
                Order.created_at.desc()
            ).offset(offset).limit(limit).all()
            
            # 转换为字典格式
            orders_list = []
            for order in orders:
                # 查询订单对应的商品信息
                order_items = session.query(OrderItem).filter(
                    OrderItem.order_id == order.id
                ).options(
                    joinedload(OrderItem.item)
                ).all()
                
                # 获取商品缩略信息
                items_info = []
                for oi in order_items:
                    if oi.item:
                        items_info.append({
                            'item_id': oi.item_id,
                            'title': oi.item.title,
                            'quantity': oi.quantity,
                            'price': float(oi.unit_price),
                            'image_url': oi.item.image_url
                        })
                
                order_dict = {
                    'id': order.id,
                    'total_amount': float(order.total_amount),
                    'status': order.status,
                    'status_text': dict(Order.STATUS_CHOICES).get(order.status, '未知'),
                    'shipping_address': order.shipping_address,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                    'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                    'items': items_info,
                    'items_count': len(items_info)
                }
                orders_list.append(order_dict)
            
            return True, {
                'orders': orders_list,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': (total + limit - 1) // limit if limit > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"获取订单列表失败: {str(e)}")
            return False, f"获取订单列表失败: {str(e)}"
    
    @staticmethod
    def get_order_detail(order_id, buyer_id):
        """获取订单详情（权限检查）"""
        try:
            session = db.session
            
            # 查询订单
            order = session.get(Order, order_id)
            if not order:
                return False, "订单不存在"
            
            # 权限检查：只能查看自己的订单
            if order.buyer_id != buyer_id:
                return False, "无权查看此订单"
            
            # 查询订单明细及商品信息
            order_items = session.query(OrderItem).filter(
                OrderItem.order_id == order_id
            ).options(
                joinedload(OrderItem.item).joinedload(Item.seller)
            ).all()
            
            # 构建详细的订单信息
            items_detail = []
            for oi in order_items:
                item_info = {
                    'order_item_id': oi.id,
                    'item_id': oi.item_id,
                    'title': oi.item.title if oi.item else '商品已删除',
                    'description': oi.item.description if oi.item else '',
                    'quantity': oi.quantity,
                    'unit_price': float(oi.unit_price),
                    'subtotal': float(oi.unit_price * oi.quantity),
                    'image_url': oi.item.image_url if oi.item else None,
                    'category': oi.item.category if oi.item else None,
                    'seller_info': {
                        'id': oi.item.seller_id if oi.item else None,
                        'username': oi.item.seller.username if oi.item and oi.item.seller else None
                    } if oi.item and oi.item.seller else None
                }
                items_detail.append(item_info)
            
            # 获取买家信息
            buyer = session.get(User, buyer_id)
            buyer_info = {
                'id': buyer.id,
                'username': buyer.username,
                'phone': buyer.phone
            } if buyer else None
            
            order_detail = {
                'id': order.id,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'status_text': dict(Order.STATUS_CHOICES).get(order.status, '未知'),
                'shipping_address': order.shipping_address,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None,
                'buyer': buyer_info,
                'items': items_detail,
                'items_count': len(items_detail)
            }
            
            return True, order_detail
            
        except Exception as e:
            logger.error(f"获取订单详情失败: {str(e)}")
            return False, f"获取订单详情失败: {str(e)}"
    
    @staticmethod
    def update_order_status(order_id, buyer_id, status):
        """更新订单状态"""
        try:
            session = db.session
            
            # 查询订单
            order = session.get(Order, order_id)
            if not order:
                return False, "订单不存在"
            
            # 权限检查：只能更新自己的订单
            if order.buyer_id != buyer_id:
                return False, "无权更新此订单"
            
            # 验证状态是否有效
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if status not in valid_statuses:
                return False, f"无效的订单状态，必须是: {', '.join(valid_statuses)}"
            
            # 状态流转规则检查
            if order.status == 'cancelled' and status != 'cancelled':
                return False, "已取消的订单不能修改状态"
            if order.status == 'completed' and status != 'completed':
                return False, "已完成的订单不能修改状态"
            
            # 只有特定状态才能被买家修改
            buyer_allowed_statuses = ['pending', 'cancelled']
            if status not in buyer_allowed_statuses and order.status in buyer_allowed_statuses:
                # 买家只能取消待支付的订单
                if status == 'cancelled' and order.status == 'pending':
                    order.status = status
                    order.updated_at = datetime.now()
                    session.commit()
                    return True, "订单已取消"
                else:
                    return False, "买家只能取消待支付的订单"
            
            # 其他状态更新（如卖家发货、完成等）
            order.status = status
            order.updated_at = datetime.now()
            session.commit()
            
            logger.info(f"订单状态更新: 订单ID={order_id}, 新状态={status}")
            return True, "订单状态更新成功"
            
        except Exception as e:
            session.rollback()
            logger.error(f"更新订单状态失败: {str(e)}")
            return False, f"更新订单状态失败: {str(e)}"
    
    @staticmethod
    def cancel_order(order_id, buyer_id):
        """
        取消订单并恢复库存
        使用事务保证库存恢复和状态更新的原子性
        """
        session = db.session
        
        try:
            # ==================== 步骤1: 查询订单并锁定 ====================
            stmt = select(Order).where(Order.id == order_id).with_for_update()
            order_result = session.execute(stmt)
            order = order_result.scalar_one_or_none()
            
            if not order:
                return False, "订单不存在"
            
            # 权限检查
            if order.buyer_id != buyer_id:
                return False, "无权取消此订单"
            
            # 状态检查：只能取消待支付的订单
            if order.status != 'pending':
                return False, "只能取消待支付的订单"
            
            # ==================== 步骤2: 查询订单明细并锁定商品 ====================
            order_items = session.query(OrderItem).filter(
                OrderItem.order_id == order_id
            ).options(
                joinedload(OrderItem.item)
            ).all()
            
            # 获取所有商品ID
            item_ids = [oi.item_id for oi in order_items]
            
            # 锁定所有相关商品
            if item_ids:
                items_stmt = select(Item).where(Item.id.in_(item_ids)).with_for_update()
                items_result = session.execute(items_stmt)
                items_dict = {item.id: item for item in items_result.scalars().all()}
            
            # ==================== 步骤3: 恢复库存 ====================
            for oi in order_items:
                if oi.item_id in items_dict:
                    item = items_dict[oi.item_id]
                    item.stock += oi.quantity
                    item.updated_at = datetime.now()
                    logger.info(f"订单取消恢复库存: 商品 {item.id} 恢复 {oi.quantity}, 当前 {item.stock}")
            
            # ==================== 步骤4: 更新订单状态 ====================
            order.status = 'cancelled'
            order.updated_at = datetime.now()
            
            # ==================== 步骤5: 提交事务 ====================
            session.commit()
            
            logger.info(f"订单取消成功: 订单ID={order_id}, 买家ID={buyer_id}")
            return True, "订单取消成功，库存已恢复"
            
        except Exception as e:
            session.rollback()
            logger.error(f"取消订单失败: {str(e)}\n{traceback.format_exc()}")
            return False, f"取消订单失败: {str(e)}"
    
    @staticmethod
    def get_addresses(user_id):
        """获取用户的配送地址列表"""
        try:
            addresses = db.session.query(Address).filter(
                Address.user_id == user_id
            ).order_by(
                Address.is_default.desc(),
                Address.created_at.desc()
            ).all()
            
            addresses_list = []
            for addr in addresses:
                addr_dict = {
                    'id': addr.id,
                    'recipient_name': addr.recipient_name,
                    'phone': addr.phone,
                    'province': addr.province,
                    'city': addr.city,
                    'district': addr.district,
                    'detail': addr.detail,
                    'is_default': addr.is_default,
                    'created_at': addr.created_at.isoformat() if addr.created_at else None,
                    'full_address': f"{addr.province or ''}{addr.city or ''}{addr.district or ''}{addr.detail}"
                }
                addresses_list.append(addr_dict)
            
            return True, addresses_list
            
        except Exception as e:
            logger.error(f"获取地址列表失败: {str(e)}")
            return False, f"获取地址列表失败: {str(e)}"
    
    @staticmethod
    def create_address(user_id, data):
        """添加新配送地址"""
        try:
            # 验证必填字段
            required_fields = ['recipient_name', 'phone', 'detail']
            for field in required_fields:
                if not data.get(field):
                    return False, f"缺少必要字段: {field}"
            
            # 如果设置为默认地址，先取消其他默认地址
            if data.get('is_default'):
                db.session.query(Address).filter(
                    Address.user_id == user_id,
                    Address.is_default == True
                ).update({'is_default': False})
            
            # 创建新地址
            address = Address(
                user_id=user_id,
                recipient_name=data['recipient_name'],
                phone=data['phone'],
                province=data.get('province'),
                city=data.get('city'),
                district=data.get('district'),
                detail=data['detail'],
                is_default=data.get('is_default', False),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(address)
            db.session.commit()
            
            return True, {
                'id': address.id,
                'recipient_name': address.recipient_name,
                'phone': address.phone,
                'province': address.province,
                'city': address.city,
                'district': address.district,
                'detail': address.detail,
                'is_default': address.is_default
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建地址失败: {str(e)}")
            return False, f"创建地址失败: {str(e)}"
    
    @staticmethod
    def update_address(user_id, address_id, data):
        """更新配送地址"""
        try:
            # 查询地址
            address = db.session.get(Address, address_id)
            if not address:
                return False, "地址不存在"
            
            # 权限检查
            if address.user_id != user_id:
                return False, "无权修改此地址"
            
            # 如果设置为默认地址，先取消其他默认地址
            if data.get('is_default'):
                db.session.query(Address).filter(
                    Address.user_id == user_id,
                    Address.is_default == True,
                    Address.id != address_id
                ).update({'is_default': False})
            
            # 更新地址字段
            updatable_fields = ['recipient_name', 'phone', 'province', 'city', 'district', 'detail', 'is_default']
            for field in updatable_fields:
                if field in data:
                    setattr(address, field, data[field])
            
            address.updated_at = datetime.now()
            db.session.commit()
            
            return True, {
                'id': address.id,
                'recipient_name': address.recipient_name,
                'phone': address.phone,
                'province': address.province,
                'city': address.city,
                'district': address.district,
                'detail': address.detail,
                'is_default': address.is_default
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新地址失败: {str(e)}")
            return False, f"更新地址失败: {str(e)}"
    
    @staticmethod
    def get_statistics(user_id):
        """获取用户的订单统计信息"""
        try:
            session = db.session
            
            stats = {
                'total_orders': 0,
                'pending_orders': 0,
                'completed_orders': 0,
                'total_spent': 0.0
            }
            
            # 获取所有订单
            orders = session.query(Order).filter(
                Order.buyer_id == user_id
            ).all()
            
            stats['total_orders'] = len(orders)
            
            # 统计各状态订单数量
            status_counts = {}
            total_spent = Decimal('0.00')
            
            for order in orders:
                status_counts[order.status] = status_counts.get(order.status, 0) + 1
                if order.status in ['paid', 'shipped', 'completed']:
                    total_spent += order.total_amount
            
            stats['pending_orders'] = status_counts.get('pending', 0)
            stats['completed_orders'] = status_counts.get('completed', 0)
            stats['total_spent'] = float(total_spent)
            
            return True, stats
            
        except Exception as e:
            logger.error(f"获取订单统计失败: {str(e)}")
            return False, f"获取订单统计失败: {str(e)}"