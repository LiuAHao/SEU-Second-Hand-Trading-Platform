# 数据库变更日志

## v2.0 (2026-01-11)

### 🎉 新增功能

#### 1. 收藏表 (favorites)
新增完整的商品收藏功能：
```sql
CREATE TABLE favorites (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_item (user_id, item_id)
);
```

### 🔧 优化改进

#### 2. 订单表 (orders) 优化
- ✅ 新增 `order_number` VARCHAR(50) - 订单号（唯一）
- ✅ 新增 `seller_id` INT - 卖家ID（外键）
- ✅ 新增 `remarks` TEXT - 订单备注
- ✅ 删除 `total_price` 冗余字段（通过订单明细计算）
- ✅ 修改 `shipping_address` 为可空字段
- ✅ 新增索引：`idx_order_number`, `idx_seller_id`

#### 3. 订单明细表 (order_items) 优化
- ✅ 统一字段命名：`price_at_purchase` → `unit_price`
- ✅ 优化索引：`idx_order_id`, `idx_item_id`

#### 4. 评价表 (reviews) 优化
- ✅ 新增唯一约束：`uk_order_id`（一个订单只能评价一次）
- ✅ 新增索引：`idx_reviewee_id`, `idx_created_at`
- ✅ 新增 CHECK 约束：评分范围 1-5

#### 5. 商品表 (items) 优化
- ✅ 新增索引：`idx_stock`, `idx_is_active`
- ✅ 更新 `favorites` 字段注释（由 favorites 表触发器更新）

#### 6. 地址表 (addresses) 优化
- ✅ 新增 `updated_at` 字段（自动更新时间戳）

### 📊 数据库表汇总

| 表名 | 记录用途 | 版本 |
|------|---------|------|
| users | 用户信息 | v1.0 |
| items | 商品信息 | v1.0 |
| **favorites** | **收藏记录** | **v2.0** ⭐ |
| orders | 订单主表 | v1.0 (v2.0优化) |
| order_items | 订单明细 | v1.0 (v2.0优化) |
| addresses | 配送地址 | v1.0 (v2.0优化) |
| reviews | 交易评价 | v1.0 (v2.0优化) |

### 🔄 迁移说明

**从 v1.0 升级到 v2.0**：
1. 备份数据库：`mysqldump -u root -p seu_second_hand > backup_v1.sql`
2. 执行迁移脚本：`mysql -u root -p seu_second_hand < migration_v1_to_v2_fixed.sql`
3. 验证迁移结果（脚本会自动输出验证信息）

**全新安装 v2.0**：
```bash
mysql -u root -p seu_second_hand < schema_optimized.sql
```

### ⚠️ 破坏性变更

- ⚠️ `orders.total_price` 字段已删除（使用 SUM(order_items.unit_price * quantity) 计算）
- ⚠️ `order_items.price_at_purchase` 重命名为 `unit_price`

### 📝 兼容性说明

- ✅ MySQL 8.0+ （推荐）
- ✅ MySQL 5.7+ （需使用 `migration_v1_to_v2_fixed.sql`）
- ⚠️ 迁移脚本已针对 MySQL 5.7 语法进行优化（避免 `IF NOT EXISTS` 等不支持的语法）

---

## v1.0 (2024-12-24)

### 初始版本
- ✅ 6 个核心表
- ✅ 完整的用户、商品、订单、评价系统
- ✅ utf8mb4_unicode_ci 字符集支持

---

**文档维护**: AI 代理自动生成  
**最后更新**: 2026-01-11
