# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import validates

# 初始化SQLAlchemy实例（后续在Flask应用中注册）
db = SQLAlchemy()

# -------------------------- 1. 用户表（Users）- 核心基础表 --------------------------
class User(db.Model):
    __tablename__ = 'users'  # 与数据库表名严格一致

    # 核心字段（匹配schema.sql，含完整约束）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希值')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱（必须为@seu.edu.cn）')
    phone = db.Column(db.String(20), nullable=True, default=None, comment='电话号码')
    avatar_url = db.Column(db.String(255), nullable=True, default=None, comment='头像URL')
    bio = db.Column(db.Text, nullable=True, default=None, comment='个人简介')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    is_active = db.Column(db.Boolean, default=True, nullable=False, comment='账户是否激活')

    # 索引定义（匹配schema.sql）
    __table_args__ = (
        db.Index('idx_username', 'username'),
        db.Index('idx_email', 'email'),
        db.Index('idx_created_at', 'created_at'),
    )

    # 模型关联关系（正向/反向查询，级联操作）
    # 1. 用户（卖家）发布的商品：user.items → 获取该用户所有商品；item.seller → 获取商品卖家
    items = db.relationship('Item', backref='seller', lazy=True, cascade='all, delete-orphan')
    # 2. 用户（买家）创建的订单：user.orders → 获取该用户所有订单；order.buyer → 获取订单买家
    orders = db.relationship('Order', backref='buyer', lazy=True, cascade='all, delete-orphan')
    # 3. 用户的收货地址：user.addresses → 获取该用户所有地址；address.user → 获取地址所属用户
    addresses = db.relationship('Address', backref='user', lazy=True, cascade='all, delete-orphan')
    # 4. 用户发布的评价（作为评价者）：user.reviews_given → 该用户给出的所有评价
    reviews_given = db.relationship('Review', backref='reviewer', foreign_keys='Review.reviewer_id', lazy=True, cascade='all, delete-orphan')
    # 5. 用户收到的评价（作为被评价者）：user.reviews_received → 该用户收到的所有评价
    reviews_received = db.relationship('Review', backref='reviewee', foreign_keys='Review.reviewee_id', lazy=True, cascade='all, delete-orphan')

    # 邮箱格式验证（必须为@seu.edu.cn）
    @validates('email')
    def validate_email(self, key, email):
        if not email.endswith('@seu.edu.cn'):
            raise ValueError('邮箱必须为东南大学邮箱（@seu.edu.cn）')
        return email

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# -------------------------- 2. 商品表（Items）- 核心业务表 --------------------------
class Item(db.Model):
    __tablename__ = 'items'  # 与数据库表名严格一致
    # 商品分类枚举（定义在类内部）
    CATEGORY_CHOICES = [
        ('books', '教材书籍'),
        ('electronics', '电子产品'),
        ('daily', '生活用品'),
        ('sports', '运动器材'),
        ('clothes', '服饰鞋帽'),
        ('other', '其他商品')
    ]
    # 核心字段（匹配schema.sql，含完整约束）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='商品ID')
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='卖家ID')
    title = db.Column(db.String(100), nullable=False, comment='商品标题')
    description = db.Column(db.Text, nullable=False, comment='商品描述')
    category = db.Column(db.String(50), nullable=False, default='other', comment='分类')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='价格')
    stock = db.Column(db.Integer, nullable=False, default=0, comment='库存数量（关键字段）')
    views = db.Column(db.Integer, nullable=False, default=0, comment='浏览次数')
    favorites = db.Column(db.Integer, nullable=False, default=0, comment='收藏次数')
    image_url = db.Column(db.String(255), nullable=True, default=None, comment='商品图片URL')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment='是否在售')

    # 索引定义（匹配schema.sql）
    __table_args__ = (
        db.Index('idx_seller_id', 'seller_id'),
        db.Index('idx_category', 'category'),
        db.Index('idx_price', 'price'),
        db.Index('idx_created_at', 'created_at'),
        # 全文索引在SQLAlchemy中通常通过数据库直接创建，此处仅做标记
        # db.Index('idx_title_description', 'title', 'description', postgresql_using='gin')
    )

    # 模型关联关系
    # 1. 商品对应的订单明细：item.order_items → 该商品被包含的所有订单明细
    order_items = db.relationship('OrderItem', backref='item', lazy=True, cascade='all, delete-orphan')
    # 2. 商品对应的评价：item.reviews → 该商品的所有评价
    reviews = db.relationship('Review', backref='item', lazy=True, cascade='all, delete-orphan')
    
    # 分类验证器
    @validates('category')
    def validate_category(self, key, category):
        valid_categories = [choice[0] for choice in self.CATEGORY_CHOICES]
        if category not in valid_categories:
            raise ValueError(f'无效分类，必须是：{", ".join(valid_categories)}')
        return category

    def to_dict(self):
        """将 Item 对象转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'price': float(self.price) if self.price else 0.0,
            'stock': self.stock,
            'seller_id': self.seller_id,
            'image_url': self.image_url,
            'views': self.views,
            'favorites': self.favorites,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'category_name': dict(self.CATEGORY_CHOICES).get(self.category, '其他')
        }

    def __repr__(self):
        return f"<Item(id={self.id}, title='{self.title}', price={self.price}, stock={self.stock}, seller_id={self.seller_id})>"

# -------------------------- 3. 订单表（Orders）- 核心业务表 --------------------------
class Order(db.Model):
    __tablename__ = 'orders'  # 与数据库表名严格一致
    # 订单状态枚举（定义在类内部）
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消')
    ]
    # 核心字段（匹配schema.sql，含完整约束）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='订单ID')
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='买家ID')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, comment='订单总金额')
    status = db.Column(db.String(50), nullable=False, default='pending', comment='订单状态')
    shipping_address = db.Column(db.String(255), nullable=False, comment='配送地址')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')

    # 索引定义（匹配schema.sql）
    __table_args__ = (
        db.Index('idx_buyer_id', 'buyer_id'),
        db.Index('idx_status', 'status'),
        db.Index('idx_created_at', 'created_at'),
    )

    # 模型关联关系
    # 1. 订单对应的明细：order.order_items → 该订单包含的所有商品明细
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    # 2. 订单对应的评价：order.reviews → 该订单对应的所有评价
    reviews = db.relationship('Review', backref='order', lazy=True, cascade='all, delete-orphan')
    
    # 状态验证器
    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = [choice[0] for choice in self.STATUS_CHOICES]
        if status not in valid_statuses:
            raise ValueError(f'无效状态，必须是：{", ".join(valid_statuses)}')
        return status

    def __repr__(self):
        return f"<Order(id={self.id}, buyer_id={self.buyer_id}, total_amount={self.total_amount}, status='{self.status}')>"

# -------------------------- 4. 订单明细表（Order_Items）- 关联表 --------------------------
class OrderItem(db.Model):
    __tablename__ = 'order_items'  # 与数据库表名严格一致

    # 核心字段（匹配schema.sql，含联合外键约束）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='订单明细ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment='订单ID')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='商品ID')
    quantity = db.Column(db.Integer, nullable=False, default=1, comment='购买数量')
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False, comment='购买时价格')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')

    # 索引定义（匹配schema.sql）
    __table_args__ = (
        db.Index('idx_order_id', 'order_id'),
        db.Index('idx_item_id', 'item_id'),
    )

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, item_id={self.item_id}, quantity={self.quantity}, price_at_purchase={self.price_at_purchase})>"

# -------------------------- 5. 地址表（Addresses）- 辅助业务表 --------------------------
class Address(db.Model):
    __tablename__ = 'addresses'  # 与数据库表名严格一致

    # 核心字段（适配收货地址业务需求）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='地址ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    recipient_name = db.Column(db.String(50), nullable=False, comment='收货人姓名')
    phone = db.Column(db.String(20), nullable=False, comment='收货人电话')  # 字段名从recipient_phone改为phone（匹配schema）
    province = db.Column(db.String(50), nullable=True, comment='省份')  # 允许为NULL（匹配schema）
    city = db.Column(db.String(50), nullable=True, comment='城市')  # 允许为NULL（匹配schema）
    district = db.Column(db.String(50), nullable=True, comment='区县')  # 允许为NULL（匹配schema）
    detail = db.Column(db.String(255), nullable=False, comment='详细地址')  # 字段名从detail_address改为detail（匹配schema）
    is_default = db.Column(db.Boolean, nullable=False, default=False, comment='是否为默认地址')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')  # 补充更新时间字段

    # 索引定义（匹配schema.sql）
    __table_args__ = (
        db.Index('idx_user_id', 'user_id'),
    )

    def __repr__(self):
        return f"<Address(id={self.id}, user_id={self.user_id}, recipient_name='{self.recipient_name}', is_default={self.is_default})>"

# -------------------------- 6. 评价表（Reviews）- 辅助业务表 --------------------------
class Review(db.Model):
    __tablename__ = 'reviews'  # 与数据库表名严格一致

    # 核心字段（适配商品评价业务需求）
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='评价ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, comment='订单ID')
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False, comment='商品ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='评价者ID')
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='被评价者ID')
    rating = db.Column(db.SmallInteger, nullable=False, comment='评分（1-5星）')
    content = db.Column(db.Text, nullable=True, default=None, comment='评价内容')
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='评价创建时间')

    # 约束与索引（匹配schema.sql）
    __table_args__ = (
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating_range'),
        db.Index('idx_item_id', 'item_id'),
        db.Index('idx_reviewer_id', 'reviewer_id'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, item_id={self.item_id}, reviewer_id={self.reviewer_id}, reviewee_id={self.reviewee_id}, rating={self.rating})>"