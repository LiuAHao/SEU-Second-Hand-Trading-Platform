-- ================================================
-- 数据库迁移脚本：从 v1.0 迁移到 v2.0（优化版）- 修复版
-- 适用场景：已有旧版数据库，需要迁移到新结构
-- 执行前请务必备份数据库！
-- 修复：移除不支持的外键 COMMENT
-- ================================================

SET NAMES utf8mb4;

-- =========================================
-- 步骤1：添加收藏表（Favorites）
-- =========================================
CREATE TABLE IF NOT EXISTS favorites (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    item_id INT NOT NULL COMMENT '商品ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_item (user_id, item_id) COMMENT '同一用户不能重复收藏同一商品',
    INDEX idx_user_id (user_id) COMMENT '用户索引',
    INDEX idx_item_id (item_id) COMMENT '商品索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收藏表';


-- =========================================
-- 步骤2：优化订单表（添加缺失字段）
-- =========================================

-- 2.1 添加 order_number 字段
-- 注意：MySQL 5.7 不支持 IF NOT EXISTS，需要手动检查
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND COLUMN_NAME = 'order_number');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE orders ADD COLUMN order_number VARCHAR(50) UNIQUE COMMENT ''订单号（唯一）'' AFTER id',
    'SELECT ''Column order_number already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.2 为已有订单生成订单号
UPDATE orders
SET order_number = CONCAT('ORD', LPAD(id, 10, '0'))
WHERE order_number IS NULL OR order_number = '';

-- 2.3 添加 seller_id 字段
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND COLUMN_NAME = 'seller_id');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE orders ADD COLUMN seller_id INT COMMENT ''卖家ID'' AFTER buyer_id',
    'SELECT ''Column seller_id already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.4 从订单明细中获取卖家ID并填充
UPDATE orders o
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN items i ON oi.item_id = i.id
SET o.seller_id = i.seller_id
WHERE o.seller_id IS NULL;

-- 2.5 添加 seller_id 外键约束
SET @constraint_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND CONSTRAINT_NAME = 'fk_orders_seller_id');

SET @sql = IF(@constraint_exists = 0,
    'ALTER TABLE orders ADD CONSTRAINT fk_orders_seller_id FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE',
    'SELECT ''Constraint fk_orders_seller_id already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.6 添加 remarks 字段
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND COLUMN_NAME = 'remarks');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE orders ADD COLUMN remarks TEXT COMMENT ''订单备注'' AFTER status',
    'SELECT ''Column remarks already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.7 删除重复的 total_price 字段（如果存在）
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND COLUMN_NAME = 'total_price');

SET @sql = IF(@col_exists > 0,
    'ALTER TABLE orders DROP COLUMN total_price',
    'SELECT ''Column total_price does not exist'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.8 修改 shipping_address 为可空
ALTER TABLE orders
MODIFY COLUMN shipping_address VARCHAR(255) NULL COMMENT '配送地址快照（冗余字段，用于保留下单时地址）';

-- 2.9 添加缺失的索引（使用条件检查，支持MySQL 5.7）
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND INDEX_NAME = 'idx_order_number');

SET @sql = IF(@index_exists = 0,
    'CREATE INDEX idx_order_number ON orders(order_number)',
    'SELECT "Index idx_order_number already exists" AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.10 添加 address_id 字段（统一命名）
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND COLUMN_NAME = 'address_id');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE orders ADD COLUMN address_id INT NULL COMMENT ''收货地址ID'' AFTER seller_id',
    'SELECT ''Column address_id already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.11 添加 address_id 索引
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND INDEX_NAME = 'idx_address_id');

SET @sql = IF(@index_exists = 0,
    'CREATE INDEX idx_address_id ON orders(address_id)',
    'SELECT "Index idx_address_id already exists" AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2.12 添加 address_id 外键约束
SET @constraint_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND CONSTRAINT_NAME = 'fk_orders_address_id');

SET @sql = IF(@constraint_exists = 0,
    'ALTER TABLE orders ADD CONSTRAINT fk_orders_address_id FOREIGN KEY (address_id) REFERENCES addresses(id)',
    'SELECT ''Constraint fk_orders_address_id already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'orders'
    AND INDEX_NAME = 'idx_seller_id');

SET @sql = IF(@index_exists = 0,
    'CREATE INDEX idx_seller_id ON orders(seller_id)',
    'SELECT "Index idx_seller_id already exists" AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =========================================
-- 步骤3：优化订单明细表（统一字段名）
-- =========================================

-- 3.1 检查并重命名字段
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'order_items'
    AND COLUMN_NAME = 'price_at_purchase');

SET @sql = IF(@col_exists > 0,
    'ALTER TABLE order_items CHANGE COLUMN price_at_purchase unit_price DECIMAL(10, 2) NOT NULL COMMENT ''购买时单价（快照）''',
    'SELECT ''Column price_at_purchase does not exist, checking unit_price...'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 如果字段名已经是 unit_price，确保注释正确
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'order_items'
    AND COLUMN_NAME = 'unit_price');

SET @sql = IF(@col_exists > 0,
    'ALTER TABLE order_items MODIFY COLUMN unit_price DECIMAL(10, 2) NOT NULL COMMENT ''购买时单价（快照）''',
    'SELECT ''Column unit_price does not exist'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3.2 统一索引名（MySQL 5.7 兼容）
-- 删除旧索引（如果存在）
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'order_items' AND INDEX_NAME = 'idx_order_items_order_id');
SET @sql = IF(@index_exists > 0, 'ALTER TABLE order_items DROP INDEX idx_order_items_order_id', 'SELECT "Index not exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'order_items' AND INDEX_NAME = 'idx_order_items_item_id');
SET @sql = IF(@index_exists > 0, 'ALTER TABLE order_items DROP INDEX idx_order_items_item_id', 'SELECT "Index not exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建新索引（如果不存在）
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'order_items' AND INDEX_NAME = 'idx_order_id');
SET @sql = IF(@index_exists = 0, 'CREATE INDEX idx_order_id ON order_items(order_id)', 'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'order_items' AND INDEX_NAME = 'idx_item_id');
SET @sql = IF(@index_exists = 0, 'CREATE INDEX idx_item_id ON order_items(item_id)', 'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =========================================
-- 步骤4：优化评价表（添加唯一约束和索引）
-- =========================================

-- 4.1 添加 order_id 唯一约束
SET @constraint_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'reviews'
    AND CONSTRAINT_TYPE = 'UNIQUE'
    AND CONSTRAINT_NAME = 'uk_order_id');

SET @sql = IF(@constraint_exists = 0,
    'ALTER TABLE reviews ADD CONSTRAINT uk_order_id UNIQUE (order_id)',
    'SELECT ''Constraint uk_order_id already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4.2 添加缺失的索引（MySQL 5.7 兼容）
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'reviews' AND INDEX_NAME = 'idx_reviewee_id');
SET @sql = IF(@index_exists = 0, 'CREATE INDEX idx_reviewee_id ON reviews(reviewee_id)', 'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'reviews' AND INDEX_NAME = 'idx_created_at');
SET @sql = IF(@index_exists = 0, 'CREATE INDEX idx_created_at ON reviews(created_at)', 'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 4.3 检查并添加 CHECK 约束
-- MySQL 8.0.16+ 支持 CHECK 约束
SET @constraint_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.CHECK_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = 'seu_second_hand'
    AND CONSTRAINT_NAME = 'chk_rating_range');

SET @sql = IF(@constraint_exists = 0,
    'ALTER TABLE reviews ADD CONSTRAINT chk_rating_range CHECK (rating >= 1 AND rating <= 5)',
    'SELECT ''Constraint chk_rating_range already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =========================================
-- 步骤5：优化商品表（添加缺失索引）
-- =========================================

-- 5.1 添加库存索引（MySQL 5.7 兼容）
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'items' AND INDEX_NAME = 'idx_stock');
SET @sql = IF(@index_exists = 0, 'CREATE INDEX idx_stock ON items(stock)', 'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5.2 添加在售状态索引（MySQL 5.7 兼容）
SET @index_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
    WHERE TABLE_SCHEMA = 'seu_second_hand' AND TABLE_NAME = 'items' AND INDEX_NAME = 'idx_is_active');
SET @sql = IF(@index_exists = 0, 'CREATE INDEX idx_is_active ON items(is_active)', 'SELECT "Index already exists" AS msg');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 5.3 更新 favorites 字段注释
ALTER TABLE items
MODIFY COLUMN favorites INT DEFAULT 0 COMMENT '收藏次数（统计用，由favorites表触发器更新）';


-- =========================================
-- 步骤6：优化地址表（添加 updated_at 字段）
-- =========================================

SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'seu_second_hand'
    AND TABLE_NAME = 'addresses'
    AND COLUMN_NAME = 'updated_at');

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE addresses ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT ''更新时间'' AFTER created_at',
    'SELECT ''Column updated_at already exists'' AS message');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;


-- =========================================
-- 步骤7：清理和优化
-- =========================================

-- 7.1 清理孤立数据（可选）
-- DELETE FROM order_items WHERE order_id NOT IN (SELECT id FROM orders);
-- DELETE FROM reviews WHERE order_id NOT IN (SELECT id FROM orders);

-- 7.2 优化表（重建索引）
OPTIMIZE TABLE users;
OPTIMIZE TABLE items;
OPTIMIZE TABLE favorites;
OPTIMIZE TABLE addresses;
OPTIMIZE TABLE orders;
OPTIMIZE TABLE order_items;
OPTIMIZE TABLE reviews;


-- =========================================
-- 迁移完成提示
-- =========================================
SELECT '========================================' AS '';
SELECT '数据库迁移完成！' AS '状态';
SELECT '版本：v2.0（优化版）' AS '版本';
SELECT '========================================' AS '';

-- 显示各表记录数
SELECT
    'users' AS '表名',
    COUNT(*) AS '记录数'
FROM users
UNION ALL
SELECT
    'items',
    COUNT(*)
FROM items
UNION ALL
SELECT
    'favorites (新增)',
    COUNT(*)
FROM favorites
UNION ALL
SELECT
    'addresses',
    COUNT(*)
FROM addresses
UNION ALL
SELECT
    'orders',
    COUNT(*)
FROM orders
UNION ALL
SELECT
    'order_items',
    COUNT(*)
FROM order_items
UNION ALL
SELECT
    'reviews',
    COUNT(*)
FROM reviews;

-- =========================================
-- 迁移后验证
-- =========================================
SELECT
    '检查 favorites 表: ' AS '迁移验证',
    IF((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'seu_second_hand' AND table_name = 'favorites') > 0, '✅ 通过', '❌ 失败') AS '结果'
UNION ALL
SELECT
    '检查 orders.order_number: ',
    IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'seu_second_hand' AND table_name = 'orders' AND column_name = 'order_number') > 0, '✅ 通过', '❌ 失败')
UNION ALL
SELECT
    '检查 orders.seller_id: ',
    IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'seu_second_hand' AND table_name = 'orders' AND column_name = 'seller_id') > 0, '✅ 通过', '❌ 失败')
UNION ALL
SELECT
    '检查 orders.total_price 已删除: ',
    IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'seu_second_hand' AND table_name = 'orders' AND column_name = 'total_price') = 0, '✅ 通过', '❌ 失败')
UNION ALL
SELECT
    '检查 order_items.unit_price: ',
    IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'seu_second_hand' AND table_name = 'order_items' AND column_name = 'unit_price') > 0, '✅ 通过', '❌ 失败')
UNION ALL
SELECT
    '检查 reviews.uk_order_id: ',
    IF((SELECT COUNT(*) FROM information_schema.table_constraints WHERE table_schema = 'seu_second_hand' AND table_name = 'reviews' AND constraint_name = 'uk_order_id') > 0, '✅ 通过', '❌ 失败');
