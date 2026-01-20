# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
from flask_migrate import Migrate
import os
# 从 models.py 导入初始化好的 SQLAlchemy 实例 db
from .models import db
# 导入路由注册函数（若你有单独的路由管理文件，如 app/routes.py）
# 若暂未创建路由文件，可先注释，后续补充
migrate = Migrate()
try:
    from .routes import register_routes
except ImportError:
    register_routes = None

# 加载 .env 环境变量文件（优先加载，避免敏感配置硬编码）
load_dotenv()

def create_app():
    """
    Flask 应用工厂函数
    负责创建、配置应用实例，注册数据库和路由
    """
    # 1. 创建 Flask 应用实例，指定模板/静态文件目录（适配项目结构）
    app = Flask(
        __name__,
        template_folder='templates',  # 若 templates 在项目根目录，用 ../ 向上定位；若在 app 目录下，直接写 'templates'
        static_folder='static'        # 静态文件目录（CSS/JS/图片），同上对应项目结构
    )

    # 2. 核心应用配置（基础配置 + 数据库配置）
    # 2.1 基础配置：支持中文、保留 JSON 键顺序
    app.config['JSON_AS_ASCII'] = False  # 关闭 ASCII 编码，确保 JSON 响应中中文正常显示
    app.config['JSON_SORT_KEYS'] = False  # 禁止 Flask 自动排序 JSON 响应的键，保持自定义顺序

    # 2.2 数据库配置（从 .env 文件读取，避免硬编码）
    # 数据库连接字符串格式：mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI',
        'mysql+pymysql://root:123456@localhost:3306/seu_second_hand?charset=utf8mb4'
    )
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'connect_args': {'charset': 'utf8mb4'}
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对象修改跟踪，消除警告、提升性能
    # 文件上传大小限制：5MB
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # 可选：开启数据库查询日志（开发环境调试用）
    # app.config['SQLALCHEMY_ECHO'] = True

    # 3. 注册 SQLAlchemy 实例（将 db 与 Flask 应用绑定）
    db.init_app(app)
    migrate.init_app(app, db)  # 初始化 Flask-Migrate，支持数据库迁移
    
    # 4. 注册所有API蓝图
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.items import items_bp
    from app.api.orders import orders_bp  # 添加订单蓝图导入
    from app.api.cart import cart_bp      # 添加购物车蓝图导入
    from app.api.favorites import favorites_bp  # 添加收藏蓝图导入
    from app.api.upload import upload_bp        # 文件上传蓝图
    from app.api.addresses import addresses_bp  # 地址蓝图

    app.register_blueprint(items_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)      # 注册订单蓝图
    app.register_blueprint(cart_bp)        # 注册购物车蓝图
    app.register_blueprint(favorites_bp)  # 注册收藏蓝图
    app.register_blueprint(upload_bp)      # 注册上传蓝图
    app.register_blueprint(addresses_bp)   # 注册地址蓝图

    print("API蓝图注册完成: auth, users, items, orders, cart, favorites, upload, addresses")  # 添加日志

    # 5. 注册路由（若存在路由注册函数）
    if register_routes is not None:
        register_routes(app)
        print("页面路由注册成功！")

    # 6. 返回配置完整的应用实例
    return app