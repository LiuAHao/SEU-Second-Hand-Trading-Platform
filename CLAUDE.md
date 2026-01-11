# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **SEU Second-Hand Trading Platform** (东南大学校园二手交易平台) - a campus-focused e-commerce platform built for Southeast University. It enables students and faculty to buy/sell second-hand goods with campus email verification.

**Tech Stack:**
- **Backend:** Python Flask 2.3.3, Flask-SQLAlchemy, Flask-Login, MySQL 8.0+
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), component-based architecture
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
# 创建数据库（示例库名）
# mysql -u root -p -e "CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 推荐导入：v2.0 完整结构（含 favorites、order_number、seller_id、unit_price 等字段）
mysql -u root -p seu_second_hand < database/schema_optimized.sql

# 如果是旧版 6 表库，先备份再执行迁移
# mysqldump -u root -p seu_second_hand > backup.sql
# mysql -u root -p seu_second_hand < database/migration_v1_to_v2_fixed.sql

# 加载测试数据（可选）
mysql -u root -p seu_second_hand < database/seed_data.sql
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

**Templates** (Jinja2 with base template inheritance):
- `base.html` - Base template with navigation, footer, common scripts
- `index.html` - Homepage with featured items and categories
- `items.html` - Search/browse with filters (category, price, sort)
- `item_detail.html` - Individual item details
- `login.html` / `register.html` - Authentication with @seu.edu.cn validation
- `cart.html` - Session-based shopping cart
- `checkout.html` - Order placement with address selection
- `profile.html` - User profile and order history

**Important Architecture Pattern: Three-Tier Design**
This project strictly follows the three-tier architecture:

1. **API Layer** (`app/api/`): HTTP request/response handling only
   - Uses `@auth_required` decorator for protected routes
   - Uses `@validate_request` decorator for input validation
   - Delegates all business logic to services layer

2. **Service Layer** (`app/services/`): Business logic implementation
   - `OrderService`: Most complex service with transaction handling
   - `UserService`, `ItemService`, `ReviewService`, `CartService`
   - All database operations and business rules here

3. **Model Layer** (`app/models.py`): Data models and ORM relationships
  - 7 tables: User, Item, Favorite, Order, OrderItem, Address, Review
  - Uses SQLAlchemy 2.0+ with modern declarative syntax

**Critical Transaction Handling Pattern (order_service.py:30-231)**
The order creation is the most complex operation:
- Uses `with_for_update()` to lock inventory rows
- Validates stock, permissions, and business rules atomically
- Commits only after all validations pass
- Automatic rollback on any exception
- Prevents race conditions in high-concurrent scenarios

### Key Implementation Status (关键实现状态)

#### ✅ Completed (已完成)

**Backend Models & Database:**
- 6 core tables with full ORM relationships: User, Item, Order, OrderItem, Address, Review
- Input validation decorators (@validates)
- Category & Status enum choices in models
- Foreign key constraints and cascade delete

**API Layer (RESTful Endpoints):**
- **Auth Module** (`/api/user/*`):
  - POST `/api/user/register` - User registration with email validation
  - POST `/api/user/login` - Login with JWT token generation
  - POST `/api/user/logout` - Logout endpoint
  - GET `/api/user/checkUsername/{username}` - Check username availability
  - GET `/api/user/checkEmail/{email}` - Check email availability
  
- **Items Module** (`/api/item/*`):
  - GET `/api/item/getFeatured` - Featured items (for homepage)
  - POST `/api/item/search` - Advanced search (by title/seller/category + filters)
  - POST `/api/item/getByCategory` - Browse by category
  - GET `/api/item/getDetail/{itemId}` - Item details
  - POST `/api/item/publish` - Publish new item
  - PUT `/api/item/update/{itemId}` - Update item
  - DELETE `/api/item/delete/{itemId}` - Delete item
  
- **Users Module** (`/api/users/*`):
  - GET `/api/users/current` - Get current user info (auth_required)
  - GET `/api/users/{userId}/profile` - Get user profile
  - PUT `/api/users/profile` - Update profile (auth_required)

**Services Layer (Business Logic):**
- `UserService`: register_user, login_user, get_user_info, update_profile, get_user_rating
- `ItemService`: get_featured_items, search_items, get_item_by_category, get_item_detail, publish_item, etc.
- `CartService`: cart management (session-based)
- `ReviewService`: review operations

**Middleware & Utils:**
- `APIResponse` class: Unified response format (code, message, data, timestamp)
- `JWT Helper`: Token generation (HS256, 168-hour expiry), verification
- `Password Helper`: bcrypt hashing with salt (rounds=12)
- `Auth Middleware`: @auth_required decorator for protected routes
- `Error Handler`: Global exception handling with proper status codes

**Frontend Integration:**
- Mock API system for independent frontend testing
- API client with retry logic and error classification
- Form validation (SEU email format, password strength)
- Session-based shopping cart
- Notification system (toast messages)

#### ✅ Completed (已完成)

**Order Management (`/api/orders/*`):**
- Order creation with complete transaction handling (order_service.py:30-231)
- Order cancellation with stock rollback using row-level locks (order_service.py:423-484)
- Order listing, detail retrieval, and status updates
- Address CRUD operations (create, update, list)
- Order statistics and pagination
- Prevents overselling with `SELECT FOR UPDATE` locks
- Full atomic transaction support with rollback on errors

### Database Configuration (数据库配置)

**Current Database Credentials:**
- Username: `root`
- Password: `123456`
- Database Name: `seu_second_hand`
- Charset: `utf8mb4_unicode_ci`

Database URI in `app/__init__.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/seu_second_hand?charset=utf8mb4'
```

Required MySQL setup:
```bash
# Create database with UTF-8 support
mysql> CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Load schema (no comments version for cleaner import)
mysql -u root -proot seu_second_hand < database/schema_no_comment.sql

# Or load full schema with comments
mysql -u root -proot seu_second_hand < database/schema.sql

# Verify tables created
mysql -u root -proot seu_second_hand -e "SHOW TABLES;"
# Expected: addresses, items, order_items, orders, reviews, users
```

### API Response Format (统一格式)

All endpoints return:
```json
{
  "code": 0,
  "message": "成功",
  "data": {...},
  "timestamp": 1234567890
}
```

Error codes:
- 0 = SUCCESS
- 1 = GENERAL ERROR  
- 2 = VALIDATION ERROR
- 3 = AUTH ERROR (401)
- 4 = PERMISSION ERROR (403)
- 5 = NOT FOUND (404)
- 6 = SERVER ERROR (500)
- `CartManager` - Shopping cart (sessionStorage-based)
- `AuthManager` - User authentication state
- `DOMUtils` - DOM manipulation helpers
- `LoadingManager` - Loading state management

### Database Schema

**Core Tables:**
- `users` - User accounts with bcrypt password hashing
- `items` - Product listings with full-text search on title/description
- `orders` - Order management with status tracking
- `order_items` - Order-item relationships (many-to-many)
- `addresses` - User delivery addresses
- `reviews` - Buyer/seller ratings (1-5 stars)

**Key Features:**
- Charset: `utf8mb4_unicode_ci` for Chinese/emoji support
- InnoDB engine with ACID transactions
- Foreign key cascading deletes
- Optimized indexes for search (category, price, created_at, full-text)

### API Design

**All endpoints follow this pattern:**
- Base URL: `/api`
- Request format: JSON
- Response format: `{ code: 0, message: "成功", data: {}, timestamp: 1234567890 }`
- Error handling with automatic retry (max 3 times for network/timeout)

**API Modules:**
- `API.user` - Registration, login, profile management
- `API.item` - Search, CRUD, stock checking
- `API.cart` - Add/remove/update cart items
- `API.order` - Create, list, cancel, confirm delivery
- `API.category` - Get item categories
- `API.recommend` - Popular, latest, personalized recommendations
- `API.address` - Campus delivery addresses

Full API documentation: `FRONTEND_API_DOCS.md`

## Key Implementation Details

### Authentication System
- **Email Validation:** Must be `@seu.edu.cn` domain (campus restriction)
- **Password Hashing:** Uses bcrypt for secure storage
- **Session Management:** Flask-Login with session-based auth
- **Token-based:** JWT tokens returned in login response (future implementation)

### Shopping Cart
- **Storage:** `sessionStorage` (persists across page reloads, cleared on browser close)
- **Reasoning:** Temporary cart as per project requirements (no user cart persistence)
- **Management:** `CartManager` module in `main.js` handles all cart operations

### Search Functionality
- **Full-text search:** MySQL FULLTEXT index on `items.title` and `items.description`
- **Filters:** Category, price range, sorting (latest, popular, price asc/desc)
- **Search types:** By title, seller name, or category

### Security Considerations
- **SQL Injection:** All queries use parameterized statements or SQLAlchemy ORM
- **CSRF Protection:** Flask-WTF CSRF tokens enabled
- **Input Validation:** Frontend validation + backend sanitization
- **Password Requirements:** 8+ characters, must include uppercase, lowercase, and numbers

### Campus-Specific Features
- **Email verification:** SEU email domain restriction (@seu.edu.cn)
- **Delivery addresses:** Campus building/dormitory-based addresses
- **User trust:** Campus identity provides inherent trust system

## Development Workflow

### Frontend Development
1. Enable Mock API: `window.USE_MOCK_API = true; location.reload();`
2. Modify HTML templates and JavaScript
3. Test in browser (no backend needed)
4. See `QUICK_START.md` for testing guide

### Backend Development
1. Implement API endpoints in `app/api/` modules following `FRONTEND_API_DOCS.md` spec
2. Update `app/models.py` with database models if needed
3. Register blueprints in `app/routes.py`
4. Test with real database or Mock API disabled

### Database Migrations
- Schema files in `database/` folder
- `schema.sql` - Complete database structure
- `seed_data.sql` - Test data for development
- migrations folder for version control

## Important Files

| File | Purpose |
|------|---------|
| `run.py` | Application entry point |
| `config.py` | Flask configuration (currently minimal - needs DB config) |
| `app/__init__.py` | Flask app factory |
| `app/routes.py` | Route registration |
| `app/static/js/api.js` | Real API client (enterprise-grade with interceptors) |
| `app/static/js/mock-api.js` | Complete mock implementation for testing |
| `FRONTEND_API_DOCS.md` | Comprehensive API interface documentation |
| `QUICK_START.md` | 30-second startup guide |
| `database/schema.sql` | Complete database structure with comments |

## Configuration Notes

**Current State:**
- Debug mode enabled in `run.py` (`app.run(debug=True)`)
- JSON responses support Chinese (`app.config['JSON_AS_ASCII'] = False`)
- Database URI configured in `app/__init__.py` (not config.py)
- No `.env` file support currently configured
- No external services connected (email, payments are mock)

**Database Config Location:**
- Configuration is in `app/__init__.py`, not `config.py`
- `config.py` currently only contains comments

**To Add:**
- Environment variable support via python-dotenv
- SECRET_KEY for session encryption (currently hardcoded)
- JWT secret key configuration
- Email server config for verification emails
- Payment gateway integration (currently mock)

## Common Tasks

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific API module tests
pytest tests/test_api/test_orders_api.py -v
pytest tests/test_api/test_auth_api.py -v

# Run with coverage
pytest --cov=app tests/ --cov-report=html

# Run specific test function
pytest tests/test_api/test_orders_api.py::test_create_order -v
```

**Test Structure:**
- `tests/test_models.py` - Database model tests
- `tests/test_api/test_auth_api.py` - Authentication API tests
- `tests/test_api/test_items_api.py` - Items CRUD API tests
- `tests/test_api/test_orders_api.py` - Order management API tests (includes concurrent tests)
- `tests/conftest.py` - Pytest fixtures and test configuration

### Adding a New API Endpoint
1. Create function in appropriate `app/api/` module (auth.py, items.py, orders.py, users.py, reviews.py)
2. Use decorators: `@auth_required`, `@validate_request` for input validation
3. Follow response format: `{ code, message, data, timestamp }` using utils/response.py helpers
4. Implement business logic in `app/services/` layer, not in API routes
5. Register blueprint in `app/routes.py` if creating new module
6. Update `FRONTEND_API_DOCS.md` if user-facing

### Adding a New Page
1. Create HTML template in `app/templates/`
2. Extend `base.html` for consistent layout
3. Add route in `app/routes.py` (not in API modules)
4. Update navigation in `base.html` if needed
5. Add JavaScript in `app/static/js/` if needed

### Working with Transactions
When modifying order/inventory data, always use transactions:
```python
from app.models import db
from sqlalchemy import select

try:
    # Lock rows for update (prevents race conditions)
    stmt = select(Item).where(Item.id == item_id).with_for_update()
    result = session.execute(stmt)
    item = result.scalar_one()

    # Modify data
    item.stock -= quantity

    # Commit transaction
    db.session.commit()
except Exception as e:
    db.session.rollback()
    raise
```

### Database Query Examples
```python
# Using SQLAlchemy ORM
from app.models import User, Item, Order
from sqlalchemy import select

# Get user by email
user = User.query.filter_by(email='user@seu.edu.cn').first()

# Search items with filters
items = Item.query.filter(
    Item.category == 'books',
    Item.price.between(0, 100),
    Item.is_active == True
).order_by(Item.created_at.desc()).all()

# Modern SQLAlchemy 2.0 style
stmt = select(Order).where(Order.buyer_id == user_id).order_by(Order.created_at.desc())
orders = db.session.execute(stmt).scalars().all()
```

## Testing

The project includes comprehensive test coverage:

**Backend Tests:**
- Located in `tests/` directory
- Uses pytest framework with fixtures in `conftest.py`
- Test modules mirror API structure (auth, items, orders)
- Concurrent order tests verify transaction locking works correctly
- Model tests verify ORM relationships and validations

**Frontend Testing:**
- Mock API enables full frontend testing without backend
- Browser console commands for debugging (see `QUICK_START.md`)
- Responsive design testing (mobile, tablet, desktop)
- Form validation testing

**Running All Tests:**
```bash
pytest tests/ -v --cov=app
```

See `QUICK_START.md` for detailed frontend testing procedures.

## Critical Implementation Details

### Order Transaction Flow (order_service.py)
When creating an order, the system:
1. Opens database transaction
2. Locks inventory rows with `SELECT FOR UPDATE`
3. Validates stock availability and permissions
4. Calculates total amount atomically
5. Creates order and order items records
6. Decrements inventory within same transaction
7. Commits only if all steps succeed, otherwise rolls back

This prevents:
- Overselling (multiple users buying last item simultaneously)
- Inconsistent data (order created but stock not decremented)
- Lost updates (race conditions in inventory updates)

### Authentication Flow
1. User registers with `@seu.edu.cn` email validation
2. Password hashed with bcrypt (rounds=12)
3. JWT token generated on login (HS256, 168-hour expiry)
4. Token stored in frontend and sent in Authorization header
5. `@auth_required` decorator verifies token on protected routes
6. User ID extracted from token and stored in `g.user_id`

### Error Handling Pattern
All API responses follow this format (from utils/response.py):
```python
success_response(data={}, message="成功")
error_response(message="错误信息", code=400)
not_found_response(message="资源不存在")
validation_response(errors={})
```
