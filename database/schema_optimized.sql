-- ================================================
-- 东南大学校园二手交易平台 - 优化版数据库结构
-- 字符集：utf8mb4_unicode_ci（支持中文和emoji）
-- 版本：v2.0 (优化版)
-- 更新时间：2025-01-11
-- ================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- =========================================
-- 1. 用户表 (Users)
-- =========================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱（必须为@seu.edu.cn）',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值（bcrypt）',
    phone VARCHAR(20) COMMENT '电话号码',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    bio TEXT COMMENT '个人简介',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '账户是否激活',

    INDEX idx_username (username) COMMENT '用户名索引',
    INDEX idx_email (email) COMMENT '邮箱索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- =========================================
-- 2. 商品表 (Items)
-- =========================================
DROP TABLE IF EXISTS items;
CREATE TABLE items (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
    seller_id INT NOT NULL COMMENT '卖家ID',
    title VARCHAR(100) NOT NULL COMMENT '商品标题',
    description TEXT NOT NULL COMMENT '商品描述',
    category VARCHAR(50) NOT NULL DEFAULT 'other' COMMENT '分类（books/electronics/daily/sports/clothes/other）',
    price DECIMAL(10, 2) NOT NULL COMMENT '价格',
    stock INT NOT NULL DEFAULT 0 COMMENT '库存数量（关键字段）',
    views INT DEFAULT 0 COMMENT '浏览次数',
    favorites INT DEFAULT 0 COMMENT '收藏次数（统计用）',
    image_url VARCHAR(255) COMMENT '商品图片URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否在售',

    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：卖家',
    INDEX idx_seller_id (seller_id) COMMENT '卖家索引',
    INDEX idx_category (category) COMMENT '分类索引',
    INDEX idx_price (price) COMMENT '价格索引',
    INDEX idx_stock (stock) COMMENT '库存索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引',
    INDEX idx_is_active (is_active) COMMENT '在售状态索引',
    FULLTEXT INDEX idx_title_description (title, description) COMMENT '全文搜索索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';


-- =========================================
-- 3. 收藏表 (Favorites) - 新增表
-- =========================================
DROP TABLE IF EXISTS favorites;
CREATE TABLE favorites (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '收藏ID',
    user_id INT NOT NULL COMMENT '用户ID',
    item_id INT NOT NULL COMMENT '商品ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：用户',
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE COMMENT '外键：商品',
    UNIQUE KEY uk_user_item (user_id, item_id) COMMENT '同一用户不能重复收藏同一商品',
    INDEX idx_user_id (user_id) COMMENT '用户索引',
    INDEX idx_item_id (item_id) COMMENT '商品索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收藏表';


-- =========================================
-- 4. 配送地址表 (Addresses)
-- =========================================
DROP TABLE IF EXISTS addresses;
CREATE TABLE addresses (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地址ID',
    user_id INT NOT NULL COMMENT '用户ID',
    recipient_name VARCHAR(50) NOT NULL COMMENT '收货人姓名',
    phone VARCHAR(20) NOT NULL COMMENT '收货人电话',
    province VARCHAR(50) COMMENT '省份',
    city VARCHAR(50) COMMENT '城市',
    district VARCHAR(50) COMMENT '区县',
    detail VARCHAR(255) NOT NULL COMMENT '详细地址',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否为默认地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：用户',
    INDEX idx_user_id (user_id) COMMENT '用户索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配送地址表';


-- =========================================
-- 5. 订单表 (Orders) - 优化版
-- =========================================
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    order_number VARCHAR(50) UNIQUE NOT NULL COMMENT '订单号（唯一）',
    buyer_id INT NOT NULL COMMENT '买家ID',
    seller_id INT NOT NULL COMMENT '卖家ID',
    address_id INT NOT NULL COMMENT '收货地址ID',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    status VARCHAR(50) DEFAULT 'pending' COMMENT '订单状态（pending/paid/shipped/completed/cancelled）',
    remarks TEXT COMMENT '订单备注',
    shipping_address VARCHAR(255) COMMENT '配送地址快照（冗余字段，用于保留下单时地址）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：买家',
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：卖家',
    FOREIGN KEY (address_id) REFERENCES addresses(id) COMMENT '外键：地址',
    INDEX idx_order_number (order_number) COMMENT '订单号索引',
    INDEX idx_buyer_id (buyer_id) COMMENT '买家索引',
    INDEX idx_seller_id (seller_id) COMMENT '卖家索引',
    INDEX idx_status (status) COMMENT '状态索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';


-- =========================================
-- 6. 订单明细表 (Order_Items)
-- =========================================
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单明细ID',
    order_id INT NOT NULL COMMENT '订单ID',
    item_id INT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL DEFAULT 1 COMMENT '购买数量',
    unit_price DECIMAL(10, 2) NOT NULL COMMENT '购买时单价（快照）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE COMMENT '外键：订单',
    FOREIGN KEY (item_id) REFERENCES items(id) COMMENT '外键：商品',
    INDEX idx_order_id (order_id) COMMENT '订单索引',
    INDEX idx_item_id (item_id) COMMENT '商品索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单明细表';


-- =========================================
-- 7. 评价表 (Reviews)
-- =========================================
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID',
    order_id INT NOT NULL COMMENT '订单ID',
    item_id INT NOT NULL COMMENT '商品ID',
    reviewer_id INT NOT NULL COMMENT '评价者ID',
    reviewee_id INT NOT NULL COMMENT '被评价者ID',
    rating SMALLINT NOT NULL COMMENT '评分（1-5星）',
    content TEXT COMMENT '评价内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE COMMENT '外键：订单',
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE COMMENT '外键：商品',
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：评价者',
    FOREIGN KEY (reviewee_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：被评价者',
    UNIQUE KEY uk_order_id (order_id) COMMENT '一个订单只能评价一次',
    INDEX idx_item_id (item_id) COMMENT '商品索引',
    INDEX idx_reviewer_id (reviewer_id) COMMENT '评价者索引',
    INDEX idx_reviewee_id (reviewee_id) COMMENT '被评价者索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引',
    CONSTRAINT chk_rating_range CHECK (rating >= 1 AND rating <= 5) COMMENT '评分范围约束'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评价表';

SET FOREIGN_KEY_CHECKS = 1;

-- =========================================
-- 初始化说明
-- =========================================
-- 1. 创建数据库：
--    CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--
-- 2. 导入schema：
--    mysql -u root -p seu_second_hand < database/schema_optimized.sql
--
-- 3. 导入测试数据（可选）：
--    mysql -u root -p seu_second_hand < database/seed_data.sql
--
-- 主要优化点：
-- ✅ 新增 favorites 表（用户收藏关联表）
-- ✅ 优化 orders 表（移除重复字段 total_price，添加 seller_id, order_number）
-- ✅ 统一 order_items 字段名（unit_price）
-- ✅ 添加 reviews 表唯一约束（uk_order_id）
-- ✅ 补充缺失索引（idx_stock, idx_is_active, idx_created_at等）
-- ✅ addresses 表添加 updated_at 字段
