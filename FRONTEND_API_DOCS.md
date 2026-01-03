# 东南大学二手交易平台 - 前端API文档

## 📋 文档说明

本文档为东南大学二手交易平台前端开发提供API接口参考，所有API均遵循统一的响应格式。

### 统一响应格式
```json
{
  "code": 0,
  "message": "成功",
  "data": {},
  "timestamp": 1705300200
}
```

### 状态码说明
| code | 说明 |
|------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | 参数验证错误 |
| 3 | 认证失败 |
| 4 | 权限不足 |
| 5 | 资源不存在 |
| 6 | 服务器内部错误 |

---

## 🔐 认证与授权

所有受保护的API需要在请求头中添加Authorization头：

```
Authorization: Bearer <JWT_TOKEN>
```

### 获取Token
通过登录接口获取，Token有效期为7天。

---

## 👤 用户认证模块

### 1. 用户注册
**POST** `/api/user/register`

**请求体：**
```json
{
  "username": "testuser",
  "password": "Test123!",
  "email": "testuser@seu.edu.cn",
  "phone": "13800138000"  // 可选
}
```

**参数验证：**
- 用户名：3-16字符，仅限字母/数字/下划线
- 密码：8+字符，包含大小写字母和数字
- 邮箱：必须为@seu.edu.cn格式

**响应：**
```json
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "testuser@seu.edu.cn"
  },
  "timestamp": 1705300200
}
```

### 2. 用户登录
**POST** `/api/user/login`

**请求体：**
```json
{
  "username": "testuser",
  "password": "Test123!"
}
```

**响应：**
```json
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "testuser@seu.edu.cn"
    }
  },
  "timestamp": 1705300200
}
```

### 3. 用户登出
**POST** `/api/user/logout`

**请求头：** 需要Authorization

**响应：**
```json
{
  "code": 0,
  "message": "登出成功",
  "data": {},
  "timestamp": 1705300200
}
```

---

## 🛒 订单与结账模块

### 1. 创建订单（最复杂，涉及事务处理）
**POST** `/orders/`

**请求头：** 需要Authorization

**请求体：**
```json
{
  "items": [
    {
      "item_id": 1,
      "quantity": 2
    },
    {
      "item_id": 2,
      "quantity": 1
    }
  ],
  "address_id": 1
}
```

**参数验证：**
- items: 至少包含一个商品
- item_id: 必须存在且库存充足
- quantity: 1-100之间
- 不能购买自己的商品

**响应：**
```json
{
  "code": 0,
  "message": "订单创建成功",
  "data": {
    "order_id": 1,
    "total_amount": 150.00,
    "status": "pending",
    "status_text": "待支付",
    "shipping_address": "江苏省南京市玄武区四牌楼2号",
    "created_at": "2024-01-15T10:30:00",
    "items_count": 2
  },
  "timestamp": 1705300200
}
```

**错误情况：**
- 库存不足：`商品 {title} 库存不足，剩余 {stock} 件`
- 购买自己的商品：`不能购买自己的商品: {title}`
- 并发冲突：`库存不足，请刷新页面后重试`

### 2. 获取订单列表
**GET** `/orders/?page=1&limit=10`

**请求头：** 需要Authorization

**查询参数：**
- page: 页码，默认1
- limit: 每页数量，默认10，最大100

**响应：**
```json
{
  "code": 0,
  "message": "获取订单列表成功",
  "data": {
    "orders": [
      {
        "id": 1,
        "total_amount": 150.00,
        "status": "pending",
        "status_text": "待支付",
        "shipping_address": "江苏省南京市玄武区四牌楼2号",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "items": [
          {
            "item_id": 1,
            "title": "二手教材",
            "quantity": 2,
            "price": 50.00,
            "image_url": "http://example.com/image.jpg"
          }
        ],
        "items_count": 1
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "total_pages": 3
    }
  },
  "timestamp": 1705300200
}
```

### 3. 获取订单详情
**GET** `/orders/{order_id}`

**请求头：** 需要Authorization

**响应：**
```json
{
  "code": 0,
  "message": "获取订单详情成功",
  "data": {
    "id": 1,
    "total_amount": 150.00,
    "status": "pending",
    "status_text": "待支付",
    "shipping_address": "江苏省南京市玄武区四牌楼2号",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "buyer": {
      "id": 123,
      "username": "张三",
      "phone": "13800138000"
    },
    "items": [
      {
        "order_item_id": 1,
        "item_id": 1,
        "title": "二手教材",
        "description": "九成新教材",
        "quantity": 2,
        "price_at_purchase": 50.00,
        "subtotal": 100.00,
        "image_url": "http://example.com/image.jpg",
        "category": "books",
        "seller_info": {
          "id": 456,
          "username": "李四"
        }
      }
    ],
    "items_count": 1
  },
  "timestamp": 1705300200
}
```

### 4. 更新订单状态
**PUT** `/orders/{order_id}/status`

**请求头：** 需要Authorization

**请求体：**
```json
{
  "status": "cancelled"
}
```

**允许的状态：** `pending`, `paid`, `shipped`, `completed`, `cancelled`

**响应：**
```json
{
  "code": 0,
  "message": "订单状态更新成功",
  "data": null,
  "timestamp": 1705300200
}
```

**限制：**
- 买家只能取消待支付(`pending`)的订单
- 已取消或已完成的订单不能修改状态

### 5. 取消订单
**DELETE** `/orders/{order_id}`

**请求头：** 需要Authorization

**响应：**
```json
{
  "code": 0,
  "message": "订单取消成功，库存已恢复",
  "data": null,
  "timestamp": 1705300200
}
```

**注意：**
- 只能取消待支付(`pending`)的订单
- 取消后会恢复商品库存

### 6. 获取订单统计信息
**GET** `/orders/statistics`

**请求头：** 需要Authorization

**响应：**
```json
{
  "code": 0,
  "message": "获取统计信息成功",
  "data": {
    "total_orders": 10,
    "pending_orders": 2,
    "completed_orders": 7,
    "total_spent": 1250.50
  },
  "timestamp": 1705300200
}
```

---

## 📍 配送地址管理

### 1. 获取地址列表
**GET** `/orders/addresses`

**请求头：** 需要Authorization

**响应：**
```json
{
  "code": 0,
  "message": "获取地址列表成功",
  "data": [
    {
      "id": 1,
      "recipient_name": "张三",
      "phone": "13800138000",
      "province": "江苏省",
      "city": "南京市",
      "district": "玄武区",
      "detail": "四牌楼2号",
      "is_default": true,
      "created_at": "2024-01-15T10:30:00",
      "full_address": "江苏省南京市玄武区四牌楼2号"
    }
  ],
  "timestamp": 1705300200
}
```

### 2. 创建配送地址
**POST** `/orders/addresses`

**请求头：** 需要Authorization

**请求体：**
```json
{
  "recipient_name": "张三",
  "phone": "13800138000",
  "province": "江苏省",
  "city": "南京市",
  "district": "玄武区",
  "detail": "四牌楼2号",
  "is_default": true
}
```

**参数验证：**
- recipient_name: 1-50字符
- phone: 11-20字符
- detail: 1-255字符
- province/city/district: 可选，最大50字符

**响应：**
```json
{
  "code": 0,
  "message": "地址创建成功",
  "data": {
    "id": 1,
    "recipient_name": "张三",
    "phone": "13800138000",
    "province": "江苏省",
    "city": "南京市",
    "district": "玄武区",
    "detail": "四牌楼2号",
    "is_default": true
  },
  "timestamp": 1705300200
}
```

### 3. 更新配送地址
**PUT** `/orders/addresses/{address_id}`

**请求头：** 需要Authorization

**请求体：** （可部分更新）
```json
{
  "recipient_name": "李四",
  "phone": "13900139000",
  "is_default": true
}
```

**响应：**
```json
{
  "code": 0,
  "message": "地址更新成功",
  "data": {
    "id": 1,
    "recipient_name": "李四",
    "phone": "13900139000",
    "province": "江苏省",
    "city": "南京市",
    "district": "玄武区",
    "detail": "四牌楼2号",
    "is_default": true
  },
  "timestamp": 1705300200
}
```

**注意：**
- 设置为默认地址时会自动取消其他地址的默认状态

---

## 📦 商品模块

### 1. 获取商品列表
**GET** `/api/items/?page=1&limit=20&category=books&keyword=教材`

**查询参数：**
- page: 页码
- limit: 每页数量
- category: 分类筛选
- keyword: 搜索关键词

**响应：**
```json
{
  "code": 0,
  "message": "获取商品列表成功",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "数据结构教材",
        "description": "严蔚敏版数据结构",
        "category": "books",
        "price": 45.00,
        "stock": 10,
        "seller_id": 2,
        "image_url": "http://example.com/image.jpg",
        "views": 100,
        "favorites": 20,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "category_name": "教材书籍"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "total_pages": 3
    }
  },
  "timestamp": 1705300200
}
```

**商品分类：**
- `books`: 教材书籍
- `electronics`: 电子产品
- `daily`: 生活用品
- `sports`: 运动器材
- `clothes`: 服饰鞋帽
- `other`: 其他商品

---

## ⚠️ 错误处理示例

### 1. 参数验证错误
```json
{
  "code": 2,
  "message": "参数验证失败",
  "data": {
    "errors": {
      "username": "用户名需3-16字符，仅限字母、数字、下划线",
      "email": "邮箱必须为@seu.edu.cn格式"
    }
  },
  "timestamp": 1705300200
}
```

### 2. 认证失败
```json
{
  "code": 3,
  "message": "认证失败",
  "data": null,
  "timestamp": 1705300200
}
```

### 3. 权限不足
```json
{
  "code": 4,
  "message": "无权查看此订单",
  "data": null,
  "timestamp": 1705300200
}
```

### 4. 资源不存在
```json
{
  "code": 5,
  "message": "订单不存在",
  "data": null,
  "timestamp": 1705300200
}
```

### 5. 业务逻辑错误
```json
{
  "code": 400,
  "message": "不能购买自己的商品: 数据结构教材",
  "data": null,
  "timestamp": 1705300200
}
```

---

## 🔒 安全注意事项

### 1. 并发控制
- 订单创建使用数据库行级锁(`SELECT FOR UPDATE`)
- 防止库存超卖
- 建议前端在创建订单时添加防重复提交

### 2. 数据权限
- 用户只能查看和操作自己的订单
- 地址管理仅限当前用户
- 严格的身份验证和授权检查

### 3. 输入验证
- 所有输入参数都经过严格验证
- 使用统一的验证装饰器
- 防止SQL注入和XSS攻击

---

## 🚀 快速开始示例

### 创建订单完整流程：
```javascript
// 1. 登录获取Token
const loginResponse = await fetch('/api/user/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'testuser',
    password: 'Test123!'
  })
});

const { data: { token } } = await loginResponse.json();

// 2. 创建配送地址
const addressResponse = await fetch('/orders/addresses', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    recipient_name: '张三',
    phone: '13800138000',
    province: '江苏省',
    city: '南京市',
    district: '玄武区',
    detail: '四牌楼2号',
    is_default: true
  })
});

const { data: { id: addressId } } = await addressResponse.json();

// 3. 创建订单
const orderResponse = await fetch('/orders/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    items: [
      { item_id: 1, quantity: 1 },
      { item_id: 2, quantity: 2 }
    ],
    address_id: addressId
  })
});

const orderData = await orderResponse.json();
console.log('订单创建成功:', orderData);
```

---
