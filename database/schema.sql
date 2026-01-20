-- 基础建表脚本（MySQL 8+，utf8mb4_unicode_ci）
-- 如需调整库名，先手动执行：CREATE DATABASE IF NOT EXISTS seu_secondhand DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 再执行：USE seu_secondhand;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱（@seu.edu.cn）',
  phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
  avatar_url VARCHAR(255) DEFAULT NULL COMMENT '头像',
  bio TEXT DEFAULT NULL COMMENT '个人简介',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  INDEX idx_users_username (username),
  INDEX idx_users_email (email),
  INDEX idx_users_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 地址表
CREATE TABLE IF NOT EXISTS addresses (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地址ID',
  user_id INT NOT NULL COMMENT '用户ID',
  recipient_name VARCHAR(50) NOT NULL COMMENT '收货人姓名',
  phone VARCHAR(20) NOT NULL COMMENT '收货人电话',
  province VARCHAR(50) DEFAULT NULL COMMENT '省',
  city VARCHAR(50) DEFAULT NULL COMMENT '市',
  district VARCHAR(50) DEFAULT NULL COMMENT '区/校区',
  detail VARCHAR(255) NOT NULL COMMENT '详细地址',
  is_default TINYINT(1) NOT NULL DEFAULT 0 COMMENT '默认地址',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_address_user (user_id),
  CONSTRAINT fk_addresses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 商品表
CREATE TABLE IF NOT EXISTS items (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
  seller_id INT NOT NULL COMMENT '卖家ID',
  title VARCHAR(100) NOT NULL COMMENT '标题',
  description TEXT NOT NULL COMMENT '描述',
  category VARCHAR(50) NOT NULL DEFAULT 'other' COMMENT '分类',
  price DECIMAL(10,2) NOT NULL COMMENT '价格',
  stock INT NOT NULL DEFAULT 0 COMMENT '库存',
  views INT NOT NULL DEFAULT 0 COMMENT '浏览次数',
  favorites INT NOT NULL DEFAULT 0 COMMENT '收藏次数',
  image_url VARCHAR(255) DEFAULT NULL COMMENT '图片',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否在售',
  INDEX idx_seller_id (seller_id),
  INDEX idx_category (category),
  INDEX idx_price (price),
  INDEX idx_stock (stock),
  INDEX idx_created_at (created_at),
  INDEX idx_is_active (is_active),
  CONSTRAINT fk_items_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 收藏表
CREATE TABLE IF NOT EXISTS favorites (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '收藏ID',
  user_id INT NOT NULL COMMENT '用户ID',
  item_id INT NOT NULL COMMENT '商品ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
  UNIQUE KEY uk_user_item (user_id, item_id),
  INDEX idx_user_id (user_id),
  INDEX idx_item_id (item_id),
  INDEX idx_created_at (created_at),
  CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_fav_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
  order_number VARCHAR(50) NOT NULL UNIQUE COMMENT '订单号',
  buyer_id INT NOT NULL COMMENT '买家ID',
  seller_id INT NOT NULL COMMENT '卖家ID',
  address_id INT NOT NULL COMMENT '收货地址ID',
  total_amount DECIMAL(10,2) NOT NULL COMMENT '总金额',
  status VARCHAR(50) NOT NULL DEFAULT 'pending' COMMENT '状态',
  remarks TEXT DEFAULT NULL COMMENT '备注',
  shipping_address VARCHAR(255) DEFAULT NULL COMMENT '配送地址快照',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_order_number (order_number),
  INDEX idx_buyer_id (buyer_id),
  INDEX idx_seller_id (seller_id),
  INDEX idx_status (status),
  INDEX idx_order_created (created_at),
  CONSTRAINT fk_orders_buyer FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_orders_seller FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_orders_address FOREIGN KEY (address_id) REFERENCES addresses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 订单明细表
CREATE TABLE IF NOT EXISTS order_items (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单明细ID',
  order_id INT NOT NULL COMMENT '订单ID',
  item_id INT NOT NULL COMMENT '商品ID',
  quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
  unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_order_id (order_id),
  INDEX idx_item_id (item_id),
  CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_order_items_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 评价表
CREATE TABLE IF NOT EXISTS reviews (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID',
  order_id INT NOT NULL COMMENT '订单ID',
  item_id INT NOT NULL COMMENT '商品ID',
  reviewer_id INT NOT NULL COMMENT '评价人ID',
  reviewee_id INT NOT NULL COMMENT '被评价人ID',
  rating INT NOT NULL DEFAULT 5 COMMENT '评分',
  content TEXT DEFAULT NULL COMMENT '内容',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_reviews_order (order_id),
  INDEX idx_reviews_item (item_id),
  INDEX idx_reviews_reviewer (reviewer_id),
  INDEX idx_reviews_reviewee (reviewee_id),
  CONSTRAINT fk_reviews_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_reviews_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
  CONSTRAINT fk_reviews_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_reviews_reviewee FOREIGN KEY (reviewee_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
