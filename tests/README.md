# 测试文档

## 测试概述

本项目包含完整的测试套件，覆盖单元测试、API测试、服务层测试和集成测试。

### 测试结构

```
tests/
├── conftest.py                 # pytest配置和fixtures
├── __init__.py
├── test_models.py              # 数据库模型测试
├── test_routes.py              # 路由测试
├── test_api/                   # API层测试
│   ├── __init__.py
│   ├── test_auth_api.py        # 认证API测试
│   ├── test_cart_api.py        # 购物车API测试
│   ├── test_items_api.py       # 商品API测试
│   └── test_orders_api.py      # 订单API测试（重点：事务、并发）
├── test_services/              # 服务层测试
│   ├── __init__.py
│   └── test_order_service.py   # 订单服务测试（重点：业务逻辑）
└── test_integration/           # 集成测试
    ├── __init__.py
    └── test_complete_flows.py  # 完整业务流程测试
```

## 快速开始

### 运行所有测试

```bash
# 基础运行
pytest tests/ -v

# 显示详细输出和print语句
pytest tests/ -v -s

# 运行特定测试文件
pytest tests/test_api/test_orders_api.py -v

# 运行特定测试类
pytest tests/test_api/test_orders_api.py::TestOrderCreation -v

# 运行特定测试函数
pytest tests/test_api/test_orders_api.py::TestOrderCreation::test_create_order_success_single_item -v
```

### 生成覆盖率报告

```bash
# 生成终端覆盖率报告
pytest tests/ --cov=app --cov-report=term

# 生成HTML覆盖率报告
pytest tests/ --cov=app --cov-report=html

# 生成XML覆盖率报告（用于CI/CD）
pytest tests/ --cov=app --cov-report=xml
```

覆盖率报告将生成在 `htmlcov/` 目录中，打开 `htmlcov/index.html` 查看详细报告。

## 测试分类

### 1. 单元测试

**模型测试** (`test_models.py`)
- 测试数据库模型的验证规则
- 测试模型关系（外键、级联删除等）
- 测试模型方法

**路由测试** (`test_routes.py`)
- 测试页面路由是否正确响应
- 测试路由权限控制

### 2. API测试

**认证API测试** (`test_auth_api.py`)
- 用户注册：@seu.edu.cn邮箱验证、密码强度、重复检查
- 用户登录：用户名/邮箱登录、错误密码处理
- 用户登出：token验证
- 用户名/邮箱可用性检查

**商品API测试** (`test_items_api.py`)
- 商品发布、更新、删除
- 商品搜索、分类浏览
- 商品详情查询
- 权限验证（只能操作自己的商品）

**订单API测试** (`test_orders_api.py`) ⭐重点
- **订单创建**：单商品、多商品、库存验证
- **并发控制**：防止超卖（使用线程模拟并发）
- **事务处理**：验证库存原子性扣减
- **订单取消**：库存恢复、权限验证
- **地址管理**：CRUD操作、默认地址设置

**购物车API测试** (`test_cart_api.py`)
- 添加/删除/更新购物车商品
- 购物车数量计算
- 购物车清空

### 3. 服务层测试

**订单服务测试** (`test_order_service.py`) ⭐重点
直接测试 `OrderService` 的业务逻辑：

- `create_order()`: 订单创建逻辑
  - 库存锁定 (`SELECT FOR UPDATE`)
  - 事务原子性
  - 业务规则验证（不能购买自己的商品等）
  - 错误处理和回滚

- `cancel_order()`: 订单取消逻辑
  - 库存恢复
  - 状态验证
  - 事务一致性

- `get_orders()`, `get_order_detail()`: 查询逻辑
- `update_order_status()`: 状态更新逻辑
- 地址管理方法

**并发测试** ⭐重点
- 多线程同时购买最后一个商品
- 验证只有一个请求成功
- 验证库存不会变为负数
- 验证事务隔离级别

### 4. 集成测试

**完整业务流程测试** (`test_complete_flows.py`)
端到端测试，模拟真实用户场景：

- 用户注册登录流程
- 商品浏览→搜索→查看详情→下单流程
- 多商品购买流程
- 订单生命周期流程（创建→支付→发货→完成）
- 订单取消流程
- 卖家发布商品流程
- 地址管理流程
- 并发购买场景
- 评价流程
- 个人资料管理流程

## 测试Fixtures

### 核心Fixtures（conftest.py）

```python
app               # Flask应用实例
client            # 测试客户端
init_database     # 完整的测试数据集
auth_headers      # 认证请求头（user1）
auth_headers_user2  # 认证请求头（user2）
auth_headers_user3  # 认证请求头（user3）
```

### 测试数据

`init_database` fixture 提供完整的测试数据：

- **用户**: 3个测试用户（testuser1, testuser2, testuser3）
- **商品**: 6个测试商品（不同分类、不同库存）
- **地址**: 3个测试地址
- **订单**: 2个测试订单（不同状态）
- **订单明细**: 2个订单明细记录
- **评价**: 1个测试评价

## 关键测试场景

### 1. 防止超卖测试

**测试文件**: `tests/test_api/test_orders_api.py::TestOrderConcurrency`

```python
def test_concurrent_orders_no_oversell_single_item():
    """
    测试场景：
    - 商品库存：1件
    - 并发请求：2个用户同时购买
    - 预期结果：只有1个成功，另1个失败（库存不足）
    - 验证点：
      1. 成功订单数 <= 1
      2. 失败订单数 >= 1
      3. 最终库存 = 0
      4. 库存不会变为负数
    """
```

### 2. 事务回滚测试

**测试文件**: `tests/test_services/test_order_service.py::TestOrderServiceTransactions`

```python
def test_transaction_rollback_on_error():
    """
    测试场景：
    - 创建会失败的订单（库存不足）
    - 预期结果：
      1. 订单创建失败
      2. 库存未改变
      3. 数据库无脏数据
    - 验证点：事务原子性
    """
```

### 3. 订单取消库存恢复测试

**测试文件**: `tests/test_services/test_order_service.py::TestOrderServiceCancellation`

```python
def test_cancel_order_stock_restoration():
    """
    测试场景：
    - 创建订单（购买3件，库存5→2）
    - 取消订单
    - 预期结果：库存恢复为5
    - 验证点：
      1. 订单状态改为cancelled
      2. 库存完全恢复
      3. 订单明细记录保持
    """
```

### 4. 权限验证测试

**测试文件**: 多个

```python
def test_unauthorized_operations():
    """
    测试场景：
    - 用户A尝试修改用户B的订单
    - 用户A尝试使用用户B的地址
    - 用户A尝试更新用户B的商品
    - 预期结果：所有操作返回403或400
    """
```

## 运行特定测试

### 按类型运行

```bash
# 只运行API测试
pytest tests/test_api/ -v

# 只运行服务层测试
pytest tests/test_services/ -v

# 只运行集成测试
pytest tests/test_integration/ -v

# 只运行并发测试
pytest tests/ -k "concurrent" -v

# 只运行事务测试
pytest tests/ -k "transaction" -v
```

### 按模块运行

```bash
# 订单相关测试
pytest tests/ -k "order" -v

# 认证相关测试
pytest tests/ -k "auth" -v

# 商品相关测试
pytest tests/ -k "item" -v
```

## 测试最佳实践

### 1. 测试命名规范

```python
# ✅ 好的命名
def test_create_order_success_with_single_item()
def test_create_order_failure_insufficient_stock()
def test_concurrent_orders_no_oversell()

# ❌ 不好的命名
def test_order()
def test1()
def create_order_test()
```

### 2. 测试结构（AAA模式）

```python
def test_something():
    # Arrange（准备测试数据）
    item = init_database['items'][0]
    address = init_database['addresses'][0]

    # Act（执行被测试的操作）
    response = client.post('/api/orders/', json={...})

    # Assert（验证结果）
    assert response.status_code == 200
    assert response.json()['data']['order_id'] > 0
```

### 3. 测试隔离

- 每个测试应该独立运行
- 不依赖其他测试的执行顺序
- 使用fixtures提供测试数据
- 测试后自动清理数据

### 4. 测试覆盖

正常路径：
- ✅ 成功创建订单
- ✅ 成功查询订单
- ✅ 成功取消订单

异常路径：
- ✅ 库存不足
- ✅ 商品不存在
- ✅ 地址不存在
- ✅ 权限不足
- ✅ 参数验证失败

边界情况：
- ✅ 库存恰好等于购买数量
- ✅ 购买数量为0
- ✅ 购买数量为负数
- ✅ 购买数量超出限制
- ✅ 特殊字符、emoji

## 持续集成

### GitHub Actions示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 常见问题

### Q: 测试失败怎么办？

1. 查看详细错误信息：
   ```bash
   pytest tests/test_api/test_orders_api.py::TestOrderCreation::test_create_order_success -vv
   ```

2. 查看print输出：
   ```bash
   pytest tests/ -v -s
   ```

3. 只运行失败的测试：
   ```bash
   pytest tests/ --lf
   ```

### Q: 如何调试单个测试？

```bash
# 使用pdb调试
pytest tests/ --pdb

# 只在失败时进入pdb
pytest tests/ --pdb --trace
```

### Q: 并发测试不稳定怎么办？

并发测试可能因为执行速度不同而产生不同结果。可以：
1. 增加线程延迟
2. 使用固定顺序执行
3. 重试测试多次

### Q: 测试数据库在哪里？

测试使用SQLite内存数据库，测试结束后自动清理。无需手动管理。

## 测试覆盖率目标

- **总体覆盖率**: >= 80%
- **核心模块（订单、认证）**: >= 90%
- **API层**: >= 85%
- **服务层**: >= 90%

当前覆盖率可通过以下命令查看：
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

## 贡献指南

添加新测试时：

1. 确定测试类型（单元/API/集成）
2. 选择合适的测试文件
3. 遵循命名规范
4. 提供清晰的docstring
5. 确保测试独立可运行
6. 更新此文档

## 参考资源

- [Pytest官方文档](https://docs.pytest.org/)
- [Flask测试文档](https://flask.palletsprojects.com/en/latest/testing/)
- [SQLAlchemy测试](https://docs.sqlalchemy.org/en/20/orm/persistence_techniques.html#unitofwork-transaction-management)
