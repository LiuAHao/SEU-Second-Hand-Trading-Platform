"""
用户业务逻辑服务层
负责处理用户注册、登录、资料查询/更新等核心业务逻辑
"""
from app.models import User, Item, Order, OrderItem, Review, db 
from app.utils.password_helper import PasswordHelper
from app.utils.jwt_helper import generate_token
from datetime import datetime

class UserService:
    """用户服务类"""

    # -------------------------- 1. 用户注册 --------------------------
    @staticmethod
    def register_user(username: str, email: str, password: str):
        """
        用户注册业务逻辑
        :param username: 用户名
        :param email: 邮箱
        :param password: 原始密码
        :return: 业务处理结果
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': '用户名已存在'}
        
        # 检查邮箱是否已注册
        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': '邮箱已注册'}
        
        # 密码加密
        password_hash = PasswordHelper.hash_password(password)
        
        # 创建用户
        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.session.add(user)
            db.session.commit()
            
            # 返回成功结果（包含用户核心信息）
            return {
                'success': True,
                'data': {
                    'userId': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'注册失败：{str(e)}'}

    # -------------------------- 2. 用户登录 --------------------------
    @staticmethod
    def login_user(username_or_email: str, password: str):
        """
        用户登录业务逻辑
        :param username_or_email: 用户名或邮箱
        :param password: 原始密码
        :return: 业务处理结果
        """
        # 查询用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        # 验证用户是否存在
        if not user:
            return {'success': False, 'message': '用户名或密码错误'}
        
        # 验证密码
        if not PasswordHelper.verify_password(password, user.password_hash):
            return {'success': False, 'message': '用户名或密码错误'}
        
        # 验证账户是否激活
        if not user.is_active:
            return {'success': False, 'message': '账户已被禁用，请联系管理员'}
        
        # 生成Token
        token = generate_token(user.id)
        
        # 组装用户信息
        user_info = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar_url or '',
            'rating': UserService._get_user_rating(user.id)
        }
        
        return {
            'success': True,
            'data': {
                'token': token,
                'user': user_info
            }
        }

    # -------------------------- 3. 获取当前用户信息 --------------------------
    @staticmethod
    def get_current_user(user_id: int):
        """
        获取当前登录用户完整信息
        :param user_id: 用户ID
        :return: 业务处理结果
        """
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        # 获取用户统计信息
        stats = UserService._get_user_stats(user_id)
        
        # 组装返回数据
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'stats': stats,
            'rating': UserService._get_user_rating(user_id)
        }
        
        return {'success': True, 'data': user_data}

    # -------------------------- 4. 获取用户资料 --------------------------
    @staticmethod
    def get_user_profile(target_user_id: int):
        """
        获取指定用户公开资料
        :param target_user_id: 目标用户ID
        :return: 业务处理结果
        """
        user = User.query.get(target_user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        # 获取用户统计信息
        stats = UserService._get_user_stats(target_user_id)
        
        # 组装公开资料（隐藏敏感信息如邮箱）
        profile_data = {
            'id': user.id,
            'username': user.username,
            'avatar': user.avatar_url or '',
            'rating': UserService._get_user_rating(target_user_id),
            'stats': stats
        }
        
        return {'success': True, 'data': profile_data}

    # -------------------------- 5. 更新个人资料 --------------------------
    @staticmethod
    def update_user_profile(user_id: int, profile_data: dict):
        """
        更新用户个人资料
        :param user_id: 用户ID
        :param profile_data: 待更新的资料（nickname/bio/phone等）
        :return: 业务处理结果
        """
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': '用户不存在'}
        
        # 更新字段（仅更新传入的非空字段）
        if 'nickname' in profile_data and profile_data['nickname'].strip():
            # 此处nickname可映射到username，或新增nickname字段
            user.username = profile_data['nickname'].strip()
        if 'bio' in profile_data:
            user.bio = profile_data['bio'].strip()
        if 'phone' in profile_data:
            user.phone = profile_data['phone'].strip()
        if 'avatar' in profile_data and profile_data['avatar'].strip():
            user.avatar_url = profile_data['avatar'].strip()
        
        user.updated_at = datetime.now()
        
        try:
            db.session.commit()
            # 返回更新后的用户信息
            return {'success': True, 'data': UserService.get_current_user(user_id)['data']}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'更新失败：{str(e)}'}

    # -------------------------- 6. 检查用户名可用性 --------------------------
    @staticmethod
    def check_username_available(username: str):
        """
        检查用户名是否可用
        :param username: 待检查用户名
        :return: 业务处理结果
        """
        if not username.strip():
            return {'success': False, 'message': '用户名不能为空'}
        
        user = User.query.filter_by(username=username.strip()).first()
        # available为True表示可用（无重复）
        return {'success': True, 'data': {'available': user is None}}

    # -------------------------- 7. 检查邮箱可用性 --------------------------
    @staticmethod
    def check_email_available(email: str):
        """
        检查邮箱是否可用
        :param email: 待检查邮箱
        :return: 业务处理结果
        """
        if not email.strip():
            return {'success': False, 'message': '邮箱不能为空'}
        
        user = User.query.filter_by(email=email.strip()).first()
        # available为True表示可用（无重复）
        return {'success': True, 'data': {'available': user is None}}

    # -------------------------- 内部辅助方法 --------------------------
    @staticmethod
    def _get_user_rating(user_id: int) -> float:
        """
        获取用户评分（1-5分）
        :param user_id: 用户ID
        :return: 平均评分
        """
        reviews = Review.query.filter_by(reviewee_id=user_id).all()
        if not reviews:
            return 5.0  # 无评价时默认5分
        
        total_rating = sum(review.rating for review in reviews)
        return round(total_rating / len(reviews), 1)

    @staticmethod
    def _get_user_stats(user_id: int) -> dict:
        """
        获取用户统计信息
        :param user_id: 用户ID
        :return: 统计数据
        """
        # 已发布商品数
        published_count = Item.query.filter_by(seller_id=user_id, is_active=True).count()
        
        # 已售出商品数（通过订单明细关联）
        sold_subquery = db.session.query(OrderItem.item_id).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status == 'completed',
            OrderItem.item_id.in_(
                db.session.query(Item.id).filter_by(seller_id=user_id)
            )
        ).distinct()
        sold_count = sold_subquery.count()
        
        # 收藏数（此处假设Item模型有favorites字段，若需用户收藏商品数需新增关联表）
        # 暂使用商品收藏数总和，可根据实际需求调整
        favorite_count = db.session.query(db.func.sum(Item.favorites)).filter_by(seller_id=user_id).scalar() or 0
        
        return {
            'published': published_count,
            'sold': sold_count,
            'favorites': favorite_count
        }