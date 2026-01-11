# 东南大学校园二手交易平台 - AI 编码代理指南

## 项目概览

**SEU 校园二手交易平台** 是一个 Flask + MySQL + 前端的校园电商系统。核心特点：
- **用户系统**：SEU 校园邮箱（@seu.edu.cn）验证的身份认证
- **交易流程**：商品发布 → 搜索浏览 → 购物车 → 订单 → 评价
- **核心技术**：Flask 2.3.3、MySQL 8.0+（utf8mb4）、ES6 JavaScript
- **环境启动**：`python run.py` → http://localhost:5000（Debug 模式已启用）
- **数据库字符集**：必须使用 `utf8mb4_unicode_ci`（支持中文和 emoji）

## 快速环境配置

```bash
# 1. 创建虚拟环境（Windows）
python -m venv venv
venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库初始化
mysql -u root -p < database/schema.sql  # 创建所有表
mysql -u root -p < database/seed_data.sql  # 加载示例数据（可选）

# 4. 启动应用
python run.py
```

## 前端独立开发（Mock API）

在浏览器控制台执行即可切换到完整 Mock 数据：
```javascript
window.USE_MOCK_API = true; 
location.reload();
```
实现位置：[app/static/js/mock-api.js](../../app/static/js/mock-api.js) 和 [app/static/js/api.js](../../app/static/js/api.js) 第一行的条件判断

## 关键架构模式

### 1. API 响应格式（非常严格）

**所有后端 API 必须返回统一格式**。状态码严格映射（见 [app/utils/response.py](../../app/utils/response.py)）：
```json
{
  "code": 0,
  "message": "成功",
  "data": {},
  "timestamp": 1705000000
}
```

**重要约定**：
- `code: 0` = 成功（HTTP 200）
- `code: 2` = 参数验证失败（HTTP 400）
- `code: 3` = 认证失败（HTTP 401）
- `code: 4` = 权限不足（HTTP 403）
- `code: 5` = 资源不存在（HTTP 404）
- `code: 6` = 服务器错误（HTTP 500）
- `data` 始终是对象/数组（不会是 null），失败时为 `{}`
- `timestamp` 是 Unix 时间戳（整数），使用 `int(time.time())`

**使用方式**：`APIResponse.success(data=...) / APIResponse.error(code=..., message=...)`

### 2. 前后端分层架构

| 层级 | 位置 | 职责 | 例子 |
|------|------|------|------|
| **API 层** | [app/api/](../../app/api/) | RESTful 蓝图（Blueprint），HTTP 入口点 | [items.py](../../app/api/items.py)：处理 `/api/item/search` |
| **服务层** | [app/services/](../../app/services/) | 业务逻辑、数据验证、事务 | [item_service.py](../../app/services/item_service.py)：查询/过滤逻辑 |
| **模型层** | [app/models.py](../../app/models.py) | SQLAlchemy ORM，7 个表+关系（v2.0） | User, Item, Favorite, Order, OrderItem, Address, Review |
| **中间件** | [app/middleware/](../../app/middleware/) | 全局错误捕获、认证检查 | [error_handler.py](../../app/middleware/error_handler.py)：404/500 处理 |

**关键约束**：
- API 层 **只负责路由和参数解析**，业务逻辑进服务层
- 服务层返回 `{'success': bool, 'data': ..., 'message': str}` 格式
- API 层将服务结果转换为 `APIResponse`（含正确的 code/HTTP status）
- 所有蓝图在 [app/routes.py](../../app/routes.py) 的 `register_routes()` 中注册

### 3. 前端 API 调用设计

[app/static/js/api.js](../../app/static/js/api.js) 实现企业级 API 客户端（718 行）：
- **自动重试**：网络错误/超时最多重试 3 次（延迟 1 秒）
- **错误分类**：6 种错误类型（NETWORK_ERROR, TIMEOUT_ERROR, VALIDATION_ERROR 等）
- **请求拦截**：自动添加认证 token 到请求头
- **响应处理**：code 为非 0 时自动按照 ERROR_TYPES 分类
- **使用方式**：
  ```javascript
  API.user.login(email, password)
  API.item.search({query: '书', category: '教科书', page: 1, limit: 12})
  API.cart.add(itemId, quantity)
  ```

**关键实现**：[app/static/js/api.js](../../app/static/js/api.js) 第一行的条件判断决定使用真实 API 还是 Mock API

### 4. 临时购物车机制

- **存储方式**：`sessionStorage`（浏览器关闭清空）
- **管理模块**：[app/static/js/main.js](../../app/static/js/main.js) 中的 `CartManager`
- **原因**：项目需求为临时购物车，不持久化到数据库

### 5. Mock API 系统

[app/static/js/mock-api.js](../../app/static/js/mock-api.js) 提供完整模拟数据：
- **启用方式**：浏览器控制台 → `window.USE_MOCK_API = true; location.reload();`
- **用途**：前端独立开发/测试（无需后端）
- **切换机制**：条件判断选择真实 API 或 Mock API

## 编码规范

### Python 后端
1. **数据库操作**：优先使用 SQLAlchemy ORM，参数化查询防 SQL 注入
2. **响应标准**：所有端点返回 `{ code, message, data, timestamp }`
3. **错误处理**：在 [app/middleware/error_handler.py](../../app/middleware/error_handler.py) 统一捕获异常
4. **中文支持**：[app/__init__.py](../../app/__init__.py) 中已配置 `JSON_AS_ASCII = False`

### JavaScript 前端
1. **模块化**：使用 IIFE 模式，导出 `API`/`NotificationManager`/`CartManager` 等单一实例
2. **DOM 操作**：使用 `DOMUtils` 模块（在 [main.js](../../app/static/js/main.js) 中定义）
3. **表单验证**：`FormValidator` 检查 SEU 邮箱格式、密码强度等
4. **通知提示**：使用 `NotificationManager` 显示 toast 消息

### 数据库
1. **字符集**：MySQL 使用 `utf8mb4_unicode_ci`（支持中文、emoji）
2. **索引优化**：[database/schema.sql](../../database/schema.sql) 中已建立全文索引
3. **事务一致性**：订单操作需使用 InnoDB 事务保证库存一致性

## 关键文件参考

| 文件 | 核心用途 |
|------|---------|
| [config.py](../../config.py) | Flask 配置（需补充 MySQL 连接串） |
| [run.py](../../run.py) | 应用入口点 |
| [database/schema_optimized.sql](../../database/schema_optimized.sql) | 数据库完整结构（v2.0，推荐使用） |
| [database/schema.sql](../../database/schema.sql) | 数据库结构（v1.0） |
| [database/migration_v1_to_v2_fixed.sql](../../database/migration_v1_to_v2_fixed.sql) | v1→v2 迁移脚本（MySQL 5.7/8.0兼容） |
| [database/CHANGELOG.md](../../database/CHANGELOG.md) | 数据库变更历史 |
| [FRONTEND_API_DOCS.md](../../FRONTEND_API_DOCS.md) | 完整 API 接口规范（988 行） |
| [QUICK_START.md](../../QUICK_START.md) | 快速启动和测试指南 |

## 开发工作流

### 1. 添加新 API 端点

**步骤**：
1. 在 [app/services/](../../app/services/) 对应模块创建业务逻辑方法（返回 `{'success': bool, 'data': ...}` 格式）
2. 在 [app/api/](../../app/api/) 对应蓝图中创建路由函数，使用 `APIResponse.success()` / `APIResponse.error()`
3. 在 [app/routes.py](../../app/routes.py) 中注册蓝图：`app.register_blueprint(bp)`
4. 更新 [FRONTEND_API_DOCS.md](../../FRONTEND_API_DOCS.md)

**代码模板**（app/api/items.py）：
```python
@items_bp.route('/search', methods=['POST'])
def search():
    data = request.json or {}
    result = ItemService.search(...)  # 调用服务层
    if not result['success']:
        return APIResponse.error(message=result['message'])
    return APIResponse.success(data=result['data'])
```

### 2. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api/test_auth_api.py

# 运行特定测试标记（见 pytest.ini）
pytest -m api  # 只运行 API 测试
pytest -m integration  # 只运行集成测试

# 查看代码覆盖率
pytest --cov=app
```

**重要**：测试使用 SQLite 内存数据库（在 [tests/conftest.py](../../tests/conftest.py) 中配置），无需真实 MySQL

### 3. 前端独立开发

```javascript
// 浏览器控制台启用 Mock API（无需后端）
window.USE_MOCK_API = true;
location.reload();

// 现在可以测试所有前端功能
API.user.login('test@seu.edu.cn', 'password')
```

### 4. 修改数据库模型
1. 编辑 [app/models.py](../../app/models.py)（定义 SQLAlchemy 模型）
2. 更新 [database/schema.sql](../../database/schema.sql)（对应 CREATE TABLE 语句）
3. 对应的 Service 文件添加查询方法

### 5. 添加新页面模板
1. 在 [app/templates/](../../app/templates/) 创建 HTML 文件
2. 继承 `base.html`（含导航栏、页脚、公共脚本）
3. 在 [app/routes.py](../../app/routes.py) 添加路由：`@app.route('/new-page')`
4. 用 `<link>` 和 `<script>` 引入 [style.css](../../app/static/css/style.css) 和 API 模块

## 关键约束与注意事项

- ⚠️ **SEU 邮箱限制**：用户注册和登录需验证 `@seu.edu.cn` 域名
- ⚠️ **密码要求**：最少 8 字符，必须包含大小写和数字
- ⚠️ **没有外部支付接口**：支付、邮件发送目前都是模拟实现
- ⚠️ **数据库配置缺失**：[config.py](../../config.py) 需补充 MySQL 连接字符串
- ⚠️ **CSRF 防护**：已启用 Flask-WTF，表单需包含 CSRF token
- ⚠️ **全文搜索**：MySQL FULLTEXT 索引已建立在 `items.title` 和 `items.description`

## 测试方法

**前端独立测试**（不依赖后端）：
```javascript
// 浏览器控制台执行
window.USE_MOCK_API = true;
location.reload();
```

**单元测试**：运行 `pytest` 或 `pytest tests/` 

**集成测试**：启动完整应用后，使用 [QUICK_START.md](../../QUICK_START.md) 中的浏览器控制台命令

## 数据流示例

```
用户访问 /items
  ↓
模板 item_detail.html 加载
  ↓
JavaScript 调用 API.item.search() 或 API.item.getDetail()
  ↓
api.js 发送 GET /api/items/search 请求（含参数）
  ↓
app/api/items.py 接收，调用 item_service.py 业务逻辑
  ↓
item_service 查询 app/models.py 的 Item 模型
  ↓
返回 { code: 0, message: "成功", data: [...], timestamp: ... }
  ↓
api.js 拦截响应，执行本地处理
  ↓
模板动态渲染结果到 DOM
```

---

**上次更新**：2025年12月30日 | **来源**：基于 CLAUDE.md 和代码库分析
