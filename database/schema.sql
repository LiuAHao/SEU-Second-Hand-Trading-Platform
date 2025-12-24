-- 东南大学校园二手交易平台 - 数据库结构定义
-- 字符集：utf8mb4_unicode_ci（支持中文和emoji）
-- 时间：2024-12-24

-- =========================================
-- 1. 用户表 (Users)
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱（必须为@seu.edu.cn）',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    phone VARCHAR(20) COMMENT '电话号码',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    bio TEXT COMMENT '个人简介',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '账户是否激活',
    
    KEY idx_username (username) COMMENT '用户名索引',
    KEY idx_email (email) COMMENT '邮箱索引',
    KEY idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- =========================================
-- 2. 商品表 (Items)
-- =========================================
CREATE TABLE IF NOT EXISTS items (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
    seller_id INT NOT NULL COMMENT '卖家ID',
    title VARCHAR(100) NOT NULL COMMENT '商品标题',
    description TEXT NOT NULL COMMENT '商品描述',
    category VARCHAR(50) NOT NULL COMMENT '分类',
    price DECIMAL(10, 2) NOT NULL COMMENT '价格',
    stock INT NOT NULL DEFAULT 0 COMMENT '库存数量（关键字段）',
    views INT DEFAULT 0 COMMENT '浏览次数',
    favorites INT DEFAULT 0 COMMENT '收藏次数',
    image_url VARCHAR(255) COMMENT '商品图片URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否在售',
    
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：卖家',
    KEY idx_seller_id (seller_id) COMMENT '卖家索引',
    KEY idx_category (category) COMMENT '分类索引',
    KEY idx_price (price) COMMENT '价格索引',
    KEY idx_created_at (created_at) COMMENT '创建时间索引',
    FULLTEXT KEY idx_title_description (title, description) COMMENT '全文搜索索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';


-- =========================================
-- 3. 订单表 (Orders)
-- =========================================
CREATE TABLE IF NOT EXISTS orders (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    buyer_id INT NOT NULL COMMENT '买家ID',
    total_amount DECIMAL(10, 2) NOT NULL COMMENT '订单总金额',
    status VARCHAR(50) DEFAULT 'pending' COMMENT '订单状态（pending/paid/shipped/completed/cancelled）',
    shipping_address VARCHAR(255) NOT NULL COMMENT '配送地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：买家',
    KEY idx_buyer_id (buyer_id) COMMENT '买家索引',
    KEY idx_status (status) COMMENT '状态索引',
    KEY idx_created_at (created_at) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';


-- =========================================
-- 4. 订单明细表 (Order_Items)
-- =========================================
CREATE TABLE IF NOT EXISTS order_items (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单明细ID',
    order_id INT NOT NULL COMMENT '订单ID',
    item_id INT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL DEFAULT 1 COMMENT '购买数量',
    price_at_purchase DECIMAL(10, 2) NOT NULL COMMENT '购买时价格',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE COMMENT '外键：订单',
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE COMMENT '外键：商品',
    KEY idx_order_id (order_id) COMMENT '订单索引',
    KEY idx_item_id (item_id) COMMENT '商品索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单明细表';


-- =========================================
-- 5. 配送地址表 (Addresses)
-- =========================================
CREATE TABLE IF NOT EXISTS addresses (
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
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE COMMENT '外键：用户',
    KEY idx_user_id (user_id) COMMENT '用户索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='配送地址表';


-- =========================================
-- 6. 评价表 (Reviews) - 可选
-- =========================================
CREATE TABLE IF NOT EXISTS reviews (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID',
    order_id INT NOT NULL COMMENT '订单ID',
    item_id INT NOT NULL COMMENT '商品ID',
    reviewer_id INT NOT NULL COMMENT '评价者ID',
    reviewee_id INT NOT NULL COMMENT '被评价者ID',
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5) COMMENT '评分（1-5星）',
    content TEXT COMMENT '评价内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    FOREIGN KEY (order_id) REFERENCES orders(id) COMMENT '外键：订单',
    FOREIGN KEY (item_id) REFERENCES items(id) COMMENT '外键：商品',
    FOREIGN KEY (reviewer_id) REFERENCES users(id) COMMENT '外键：评价者',
    FOREIGN KEY (reviewee_id) REFERENCES users(id) COMMENT '外键：被评价者',
    KEY idx_item_id (item_id) COMMENT '商品索引',
    KEY idx_reviewer_id (reviewer_id) COMMENT '评价者索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评价表';