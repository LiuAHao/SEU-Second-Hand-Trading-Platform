# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **SEU Second-Hand Trading Platform** (东南大学校园二手交易平台) - a campus-focused e-commerce platform built for Southeast University. It enables students and faculty to buy/sell second-hand goods with campus email verification.

**Tech Stack:**
- **Backend:** Python Flask, Flask-SQLAlchemy, MySQL 8.0+
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Database:** MySQL with utf8mb4_unicode_ci charset (supports Chinese and emoji)

## Development Commands

### Starting the Application
```bash
# Windows/Mac/Linux (Direct)
python run.py
```

The app runs on `http://localhost:5000` with debug mode enabled.

### Database Setup (v2.0 推荐)
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入完整结构
mysql --default-character-set=utf8mb4 -u root -p seu_second_hand < database/schema_optimized.sql

# 旧库迁移（可选）
mysql --default-character-set=utf8mb4 -u root -p seu_second_hand < database/migration_v1_to_v2_fixed.sql

# 加载测试数据（可选）
mysql --default-character-set=utf8mb4 -u root -p seu_second_hand < database/sample_seed.sql
```

### Environment Setup
```bash
# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using Mock API for Frontend Development

The project includes a **complete Mock API system** for frontend testing without backend:

1. Start the application: `python run.py`
2. Open http://localhost:5000
3. Press **F12** to open DevTools Console
4. Run: `window.USE_MOCK_API = true; location.reload();`
5. Now all API calls return simulated data

Mock API file: `app/static/js/mock-api.js` (alternates with `app/static/js/api.js`)

## Architecture

### Backend Structure (Complete Implementation)

```
app/
├── __init__.py           # Flask app factory (create_app) - ✅ 完整实现
├── routes.py             # Main route registration - ✅ 完整实现页面路由
├── models.py             # Database models (7 tables + relationships, v2.0) - ✅ 完整实现
│                         #   • User (用户表)
│                         #   • Item (商品表)
│                         #   • Favorite (收藏表, v2.0)
│                         #   • Order (订单表: order_number, seller_id, remarks)
│                         #   • OrderItem (订单明细表: unit_price 快照)
│                         #   • Address (配送地址表)
│                         #   • Review (评价表: 订单唯一评价)
├── templates/            # Jinja2 templates (14 pages) - ✅ 完整
├── static/
│   ├── css/style.css    # Modern CSS with variables, responsive design
│   ├── js/
│   │   ├── api.js       # Real API client (enterprise-grade) - ✅ 完整实现
│   │   ├── mock-api.js  # Mock API for testing
│   │   └── main.js      # Utility modules (NotificationManager, CartManager, etc.)
│   └── images/
├── api/                 # API blueprints (RESTful endpoints) - ✅ 完整实现
│   ├── auth.py          # Authentication endpoints - ✅ register, login, logout
│   ├── cart.py          # Shopping cart endpoints
│   ├── items.py         # Item CRUD - ✅ search, featured, detail, publish
│   ├── orders.py        # Order management (✅ 部分实现)
│   ├── users.py         # User profiles - ✅ profile, check username/email
│   └── reviews.py       # Reviews and ratings
├── services/            # Business logic layer - ✅ 完整实现
│   ├── user_service.py  # User operations - ✅ register, login, profile, etc.
│   ├── item_service.py  # Item operations - ✅ search, featured, category, etc.
│   ├── order_service.py # Order operations (结构定义完整)
│   ├── cart_service.py  # Cart operations
│   └── review_service.py# Review operations
├── middleware/          # Middleware & filters - ✅ 完整实现
│   ├── auth_middleware.py  # JWT Token verification
│   ├── error_handler.py    # Global error handling
│   └── ...
└── utils/              # Utility modules - ✅ 完整实现
    ├── response.py     # Unified API response format
    ├── jwt_helper.py   # JWT token generation/verification
    ├── password_helper.py # Password hashing (bcrypt)
    ├── validators.py   # Input validation
    └── decorators.py   # Custom decorators
```

### Frontend Structure

**Templates** (Jinja2): `base.html`, `index.html`, `items.html`, `item_detail.html`, `login.html`, `register.html`, `cart.html`, `checkout.html`, `profile.html`

**Architecture Pattern:** API 层只做参数解析与返回，业务逻辑在服务层，模型层提供 ORM。

### Database Configuration (数据库配置)

数据库连接在 `app/__init__.py` 中从 `DATABASE_URI` 读取；默认库名为 `seu_second_hand`，字符集 `utf8mb4`。

### API Response Format (统一格式)

所有接口返回 `{ code, message, data, timestamp }`，详见 `app/utils/response.py`。

### API Design

接口文档见 `FRONTEND_API_DOCS.md`。

## Key Notes

- 邮箱需为 `@seu.edu.cn` 域名。
- 订单相关逻辑包含库存锁与事务处理。

## Development Workflow

### Development Workflow

详情见 `README.md` 与 `QUICK_START.md`。
