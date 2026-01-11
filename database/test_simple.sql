-- 简化版测试脚本
SET NAMES utf8mb4;
USE seu_second_hand;

-- 清空数据
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE reviews;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE favorites;
TRUNCATE TABLE addresses;
TRUNCATE TABLE items;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 创建5个用户
INSERT INTO users (username, email, password_hash, phone, bio, is_active, created_at, updated_at) VALUES
('zhangsan', 'zhangsan@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345001', '计算机学院大三学生', TRUE, NOW(), NOW()),
('lisi', 'lisi@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345002', '机械学院大四学生', TRUE, NOW(), NOW()),
('wangwu', 'wangwu@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345003', '电子学院研究生', TRUE, NOW(), NOW());

-- 创建地址
INSERT INTO addresses (user_id, recipient_name, phone, province, city, district, detail, is_default, created_at, updated_at) VALUES
(1, '张三', '13812345001', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 橘园5舍201', TRUE, NOW(), NOW()),
(2, '李四', '13812345002', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 梅园2舍305', TRUE, NOW(), NOW()),
(3, '王五', '13812345003', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 桃园7舍418', TRUE, NOW(), NOW());

-- 创建商品
INSERT INTO items (seller_id, title, description, category, price, stock, views, favorites, image_url, is_active, created_at, updated_at) VALUES
(1, '高等数学教材（同济版）', '高等数学第七版上下册，九成新', 'books', 45.00, 2, 156, 8, 'https://picsum.photos/400', TRUE, NOW(), NOW()),
(1, '小米无线鼠标', '小米便携式无线鼠标，使用4个月', 'electronics', 35.00, 1, 234, 12, 'https://picsum.photos/400', TRUE, NOW(), NOW()),
(2, '宿舍书桌台灯', '飞利浦护眼台灯，使用3年', 'daily', 45.00, 1, 123, 6, 'https://picsum.photos/400', TRUE, NOW(), NOW());

-- 创建收藏
INSERT INTO favorites (user_id, item_id, created_at) VALUES
(2, 1, NOW()),
(3, 1, NOW()),
(3, 2, NOW());

-- 创建订单
INSERT INTO orders (buyer_id, total_amount, status, shipping_address, created_at, updated_at) VALUES
(2, 45.00, 'completed', '江苏省南京市玄武区东南大学九龙湖校区 梅园2舍305', NOW(), NOW());

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(1, 1, 1, 45.00, NOW());

UPDATE items SET stock = stock - 1 WHERE id = 1;

-- 创建评价
INSERT INTO reviews (order_id, item_id, reviewer_id, reviewee_id, rating, content, created_at) VALUES
(1, 1, 2, 1, 5, '书的质量很好，笔记也很有用，卖家很耐心！', NOW());

-- 显示结果
SELECT '===== 测试数据统计 =====' AS '';
SELECT '用户' AS '类型', COUNT(*) AS '数量' FROM users
UNION ALL SELECT '商品', COUNT(*) FROM items
UNION ALL SELECT '收藏', COUNT(*) FROM favorites
UNION ALL SELECT '订单', COUNT(*) FROM orders
UNION ALL SELECT '评价', COUNT(*) FROM reviews;
