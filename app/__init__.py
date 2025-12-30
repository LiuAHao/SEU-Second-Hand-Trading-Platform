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
from app.api.cart import cart_bp
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
        'DATABASE_URI',  # 从 .env 文件读取的配置键
        # 默认值（备用，若 .env 未配置，可临时使用，生产环境需删除）
        'mysql+pymysql://root:123456@localhost:3306/SEU_Second_Hand?charset=utf8mb4'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对象修改跟踪，消除警告、提升性能
    # 可选：开启数据库查询日志（开发环境调试用）
    # app.config['SQLALCHEMY_ECHO'] = True

    # 3. 注册 SQLAlchemy 实例（将 db 与 Flask 应用绑定）
    db.init_app(app)
    migrate.init_app(app, db)  # 初始化 Flask-Migrate，支持数据库迁移
    # 注册所有API蓝图
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.items import items_bp
    app.register_blueprint(items_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    # 4. 注册路由（若存在路由注册函数）
    if register_routes is not None:
        register_routes(app)
        print("路由注册成功！")
    # 5. 返回配置完整的应用实例
    return app