# 东南大学校园二手交易平台

<p align="center">
  <img src="https://img.shields.io/badge/Flask-3.0.3-green" alt="Flask">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0.23-blue" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/MySQL-8.0-orange" alt="MySQL">
  <img src="https://img.shields.io/badge/Python-3.10+-yellow" alt="Python">
  <img src="https://img.shields.io/badge/JWT-HS256-lightgrey" alt="JWT">
</p>

## 📖 项目简介

**东南大学校园二手交易平台**是一个专为东南大学师生设计的校园内部二手商品交易系统。通过校园身份验证（@seu.edu.cn邮箱），平台为在校师生提供安全、便捷、可靠的物品流转渠道，促进校园资源循环利用，构建绿色校园生态。

### 🎯 核心价值
- **校园专属**：仅限SEU师生使用，确保交易双方身份真实性
- **资源循环**：促进教材、电子产品等校园资源的二次利用
- **安全便捷**：完整的线上交易流程，从浏览到支付的全程保障
- **教育实践**：展示完整的软件工程开发流程和技术栈应用

### ✨ 核心功能
| 模块 | 功能 | 状态 |
|------|------|------|
| ✅ **用户系统** | 校园身份注册/登录、个人资料管理、信誉评分 | 已完成 |
| ✅ **商品管理** | 商品发布/搜索/详情、分类浏览、库存管理 | 已完成 |
| ✅ **订单系统** | 购物车、订单创建/取消、状态跟踪、事务处理 | 已完成 |
| ✅ **配送管理** | 地址管理、校园配送支持 | 已完成 |
| ✅ **评价系统** | 交易评价、用户评分、信誉体系 | 已完成 |
| 🔄 **支付模拟** | 模拟支付流程、订单结算 | 开发中 |

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask 3.0.3
- **ORM**: SQLAlchemy 2.0.23
- **数据库**: MySQL 8.0+ (utf8mb4_unicode_ci)
- **认证**: JWT (HS256, 168小时有效期)
- **安全**: bcrypt (rounds=12) 密码哈希
- **部署**: Gunicorn + Nginx (生产环境)

### 前端技术栈
- **核心**: HTML5 + CSS3 + JavaScript (ES6+)
- **架构**: 响应式设计、组件化开发
- **API**: 企业级API客户端 (自动重试、错误分类)
- **测试**: Mock API系统支持独立前端开发

### 数据库设计
```sql
# 6个核心表，完整的关系设计
users       用户表     → 校园身份认证
items       商品表     → 商品信息管理
orders      订单表     → 交易记录
order_items 订单明细表 → 商品-订单关联
addresses   地址表     → 配送信息管理
reviews     评价表     → 信誉评分系统
```

## 🚀 快速开始

### 环境要求
- **Python**: 3.10+
- **MySQL**: 8.0+
- **操作系统**: Windows 10+/macOS 10.15+/Linux
- **内存**: 4GB+ (推荐8GB)
- **磁盘空间**: 2GB+

### 安装部署

#### 1. 克隆项目
```bash
git clone https://github.com/seu-trading/seu-second-hand-platform.git
cd seu-second-hand-platform
```

#### 2. 安装Python依赖
```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 配置数据库
```bash
# 1. 启动MySQL服务
# Windows
net start mysql
# macOS/Linux
sudo systemctl start mysql

# 2. 登录MySQL
mysql -u root -p

# 3. 创建数据库（在MySQL命令行中执行）
CREATE DATABASE seu_trading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

#### 4. 导入数据库结构
```bash
# 方法1：使用SQL文件
mysql -u root -p seu_trading < database/schema.sql

# 方法2：使用迁移工具
flask db upgrade
```

#### 5. 配置环境变量
```bash
# 复制配置文件
cp .env.example .env

# 编辑.env文件，配置以下信息：
# DATABASE_URI=mysql+pymysql://root:password@localhost:3306/seu_trading?charset=utf8mb4
# SECRET_KEY=your-secret-key-here
# JWT_SECRET_KEY=your-jwt-secret-key
```

#### 6. 启动应用
```bash
# 开发模式
python run.py
# 访问 http://localhost:5000

# 生产模式（推荐）
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 一键启动脚本
项目提供了便捷的启动脚本：

#### Windows
```powershell
# 使用PowerShell脚本
.\start-dev.ps1

# 或使用批处理文件
start-dev.bat
```

#### macOS/Linux
```bash
# 赋予执行权限
chmod +x start-dev.sh

# 启动
./start-dev.sh
```

## 📊 系统功能

### 🛍️ 商品系统
| 功能 | 描述 | 状态 |
|------|------|------|
| **商品发布** | 多维度发布（标题、描述、图片、价格、库存） | ✅ |
| **智能搜索** | 关键词搜索+分类筛选+价格范围+多维度排序 | ✅ |
| **分类浏览** | 6大分类：教材、电子、生活、运动、服饰、其他 | ✅ |
| **商品详情** | 完整商品信息+卖家信息+评价展示 | ✅ |
| **库存管理** | 实时库存显示、库存预警、自动扣减 | ✅ |

### 👥 用户系统
| 功能 | 描述 | 状态 |
|------|------|------|
| **校园认证** | @seu.edu.cn邮箱验证，确保身份真实性 | ✅ |
| **个人中心** | 头像、简介、联系方式、交易统计 | ✅ |
| **信誉评分** | 基于交易评价的5星评分系统 | ✅ |
| **安全认证** | JWT Token、bcrypt密码加密、权限控制 | ✅ |

### 📦 订单系统
| 功能 | 描述 | 状态 |
|------|------|------|
| **购物车** | 临时购物车（sessionStorage管理） | ✅ |
| **订单创建** | 完整事务处理，防止库存超卖 | ✅ |
| **状态跟踪** | 待支付→已支付→已发货→已完成/已取消 | ✅ |
| **地址管理** | 多地址管理，默认地址设置 | ✅ |
| **订单查询** | 订单列表、详情查看、状态筛选 | ✅ |

### ⭐ 评价系统
| 功能 | 描述 | 状态 |
|------|------|------|
| **交易评价** | 订单完成后可对商品和卖家进行评价 | ✅ |
| **评分系统** | 1-5星评分，支持文字评价 | ✅ |
| **信誉展示** | 用户信誉评分在交易中展示 | ✅ |
| **评价统计** | 商品平均评分、评价数量统计 | ✅ |

## 🔧 开发指南

### 项目结构
```
SEU-Second-Hand-Trading-Platform/
├── app/                           # 应用主目录
│   ├── __init__.py               # Flask应用工厂
│   ├── models.py                 # 数据模型（6表+关系）
│   ├── routes.py                 # 页面路由定义
│   ├── api/                      # RESTful API接口
│   │   ├── auth.py              # 认证接口
│   │   ├── items.py             # 商品接口
│   │   ├── orders.py            # 订单接口
│   │   ├── users.py             # 用户接口
│   │   └── reviews.py           # 评价接口
│   ├── services/                # 业务逻辑层
│   │   ├── order_service.py     # 订单服务（核心）
│   │   ├── item_service.py      # 商品服务
│   │   ├── user_service.py      # 用户服务
│   │   └── review_service.py    # 评价服务
│   ├── middleware/              # 中间件
│   │   ├── auth_middleware.py   # JWT认证
│   │   └── error_handler.py     # 错误处理
│   ├── utils/                   # 工具模块
│   │   ├── response.py          # 统一响应格式
│   │   ├── jwt_helper.py        # JWT工具
│   │   ├── password_helper.py   # 密码加密
│   │   ├── validators.py        # 数据验证
│   │   └── decorators.py        # 自定义装饰器
│   ├── templates/               # Jinja2模板（14个页面）
│   └── static/                  # 静态资源
├── database/                     # 数据库脚本
│   ├── schema.sql              # 数据库结构
│   └── seed_data.sql           # 测试数据
├── tests/                       # 测试代码
├── docs/                        # 项目文档
├── config.py                    # 配置文件
├── run.py                       # 应用入口
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
├── README.md                    # 项目说明
├── CLAUDE.md                    # AI开发指南
└── FRONTEND_API_DOCS.md         # API文档
```

### API开发
所有API遵循统一格式：
```json
{
  "code": 0,
  "message": "成功",
  "data": {},
  "timestamp": 1705300200
}
```

**状态码说明**：
- `0`: 成功
- `1`: 通用错误
- `2`: 参数验证错误
- `3`: 认证失败(401)
- `4`: 权限不足(403)
- `5`: 资源不存在(404)
- `6`: 服务器错误(500)

### 数据库操作示例
```python
# 使用SQLAlchemy ORM
from app.models import User, Item, Order

# 查询示例
user = User.query.filter_by(email='student@seu.edu.cn').first()
items = Item.query.filter(
    Item.category == 'books',
    Item.price.between(0, 100),
    Item.is_active == True
).order_by(Item.created_at.desc()).all()
```

### 添加新API端点
1. 在`app/api/`中创建模块
2. 实现业务逻辑
3. 在`app/__init__.py`中注册蓝图
4. 更新API文档

## 🧪 测试

### 单元测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定模块
python -m pytest tests/test_models.py -v
python -m pytest tests/test_orders.py -v

# 生成覆盖率报告
python -m pytest --cov=app tests/
```

### API测试
```bash
# 使用Python脚本测试
python tests/api_test.py

# 使用curl测试
curl -X POST http://localhost:5000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123456"}'
```

### 并发测试
```bash
# 模拟并发下单（防止超卖）
python tests/concurrent_test.py --users=10 --threads=5
```

## 🔒 安全特性

### 认证安全
- **JWT Token**: HS256算法，7天有效期
- **密码加密**: bcrypt加盐哈希，rounds=12
- **邮箱验证**: 必须为@seu.edu.cn格式
- **会话管理**: Flask-Session + 前端sessionStorage

### 数据安全
- **SQL防护**: 使用ORM，防止SQL注入
- **输入验证**: 前端+后端双重验证
- **XSS防护**: 模板自动转义
- **CSRF保护**: 启用CSRF令牌

### 业务安全
- **权限控制**: 用户只能操作自己的数据
- **事务处理**: 订单创建使用数据库事务
- **并发控制**: SELECT FOR UPDATE防止库存超卖
- **审计日志**: 记录重要操作

## 📈 性能优化

### 数据库优化
1. **索引设计**: 高频查询字段建立索引
2. **查询优化**: 使用JOIN代替子查询
3. **分页查询**: LIMIT + OFFSET分页
4. **连接池**: SQLAlchemy连接池配置

### 应用优化
1. **缓存策略**: 热点数据缓存
2. **异步处理**: 邮件发送、日志记录异步化
3. **CDN加速**: 静态资源CDN分发
4. **代码优化**: 避免N+1查询，合理使用索引

## 🚢 部署指南

### 开发环境
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动开发服务器
python run.py
```

### 生产环境
```bash
# 使用Gunicorn + Nginx
# 1. 安装Gunicorn
pip install gunicorn

# 2. 启动Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app

# 3. Nginx配置
# /etc/nginx/sites-available/seu-trading
server {
    listen 80;
    server_name seu-trading.edu.cn;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static {
        alias /path/to/app/static;
    }
}
```

### Docker部署
```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

```bash
# 构建和运行
docker build -t seu-trading .
docker run -d -p 5000:5000 --name seu-trading seu-trading
```

## 📚 文档资源

### 核心文档
| 文档 | 内容 | 链接 |
|------|------|------|
| **API文档** | 完整的API接口说明和示例 | [FRONTEND_API_DOCS.md](FRONTEND_API_DOCS.md) |
| **后端设计** | 系统架构和数据库设计 | [后端设计.md](docs/后端设计.md) |
| **开发指南** | 开发规范和最佳实践 | [CLAUDE.md](CLAUDE.md) |
| **部署手册** | 生产环境部署指南 | [DEPLOYMENT.md](docs/DEPLOYMENT.md) |

### 数据库文档
- **ER图**: `docs/ER-diagram.png`
- **Schema**: `database/schema.sql`
- **测试数据**: `database/seed_data.sql`

### 测试文档
- **测试用例**: `tests/`
- **API测试**: `tests/api_test.py`
- **并发测试**: `tests/concurrent_test.py`

## 🤝 贡献指南

### 开发流程
1. **Fork项目**
2. **创建分支**: `git checkout -b feature/your-feature`
3. **提交代码**: 遵循提交规范
4. **创建PR**: 描述更改内容和测试情况

### 代码规范
- **Python**: 遵循PEP 8，使用Black格式化
- **JavaScript**: 使用ES6+，遵循Airbnb风格
- **提交信息**: 使用约定式提交
- **文档**: 所有函数必须有docstring

### 提交规范
```
feat: 新增功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建或工具变动
```

