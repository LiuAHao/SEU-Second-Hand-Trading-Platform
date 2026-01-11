-- =========================================
-- 东南大学二手交易平台 - 真实场景测试数据
-- 模拟完整的用户交易流程
-- 密码统一为: Password123!
-- =========================================

SET NAMES utf8mb4;
USE seu_second_hand;

-- 清空现有测试数据（保留表结构）
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE reviews;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE favorites;
TRUNCATE TABLE addresses;
TRUNCATE TABLE items;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- =========================================
-- 1. 创建测试用户（5位同学）
-- =========================================
-- 密码: Password123! (bcrypt加密，rounds=12)
INSERT INTO users (username, email, password_hash, phone, bio, is_active, created_at) VALUES
('zhangsan', 'zhangsan@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345001', '计算机学院大三学生，主营二手教材和电子产品', TRUE, '2025-09-01 10:00:00'),
('lisi', 'lisi@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345002', '机械学院大四学生，清空宿舍准备毕业', TRUE, '2025-09-15 14:30:00'),
('wangwu', 'wangwu@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345003', '电子学院研究生，热爱健身和数码产品', TRUE, '2025-10-01 09:15:00'),
('zhaoliu', 'zhaoliu@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345004', '土木学院大二学生，刚搬入新宿舍需购买物品', TRUE, '2025-10-10 16:20:00'),
('sunqi', 'sunqi@seu.edu.cn', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5IdgCJqC7zQZi', '13812345005', '经管学院大三学生，喜欢购物和收集好物', TRUE, '2025-10-20 11:00:00');

-- =========================================
-- 2. 添加配送地址
-- =========================================
INSERT INTO addresses (user_id, recipient_name, phone, province, city, district, detail, is_default, created_at, updated_at) VALUES
-- 张三的地址
(1, '张三', '13812345001', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 橘园5舍201', TRUE, NOW(), NOW()),
-- 李四的地址
(2, '李四', '13812345002', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 梅园2舍305', TRUE, NOW(), NOW()),
(2, '李四（四牌楼）', '13812345002', '江苏省', '南京市', '玄武区', '东南大学四牌楼校区 30舍102', FALSE, NOW(), NOW()),
-- 王五的地址
(3, '王五', '13812345003', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 桃园7舍418', TRUE, NOW(), NOW()),
-- 赵六的地址
(4, '赵六', '13812345004', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 李园3舍210', TRUE, NOW(), NOW()),
-- 孙七的地址
(5, '孙七', '13812345005', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 桂园6舍301', TRUE, NOW(), NOW());

-- =========================================
-- 3. 发布商品（真实场景下的二手物品）
-- =========================================

-- 张三发布的商品（5件 - 主营教材和电子产品）
INSERT INTO items (seller_id, title, description, category, price, stock, views, favorites, image_url, is_active, created_at) VALUES
(1, '高等数学教材（同济版）上下册', '高等数学第七版上下册，同济大学版本。九成新，有少量笔记和标注，适合大一新生使用。原价89元/套，现价45元包邮（校内）', '教科书', 45.00, 2, 156, 8, 'https://picsum.photos/400/400?random=1', TRUE, '2025-11-01 10:30:00'),
(1, '线性代数及其应用', '线性代数及其应用（第5版），David C. Lay著。全新，只翻过几页，适合数学专业和计算机专业。', '教科书', 58.00, 1, 89, 5, 'https://picsum.photos/400/400?random=2', TRUE, '2025-11-02 14:20:00'),
(1, '小米无线鼠标', '小米便携式无线鼠标，蓝牙+2.4G双模，使用4个月，功能完好，赠送USB接收器。', '数码配件', 35.00, 1, 234, 12, 'https://picsum.photos/400/400?random=3', TRUE, '2025-11-05 09:15:00'),
(1, 'USB-C扩展坞 7合1', '绿联7合1扩展坞，支持HDMI 4K输出、3个USB3.0、SD卡槽、PD充电。全新未拆封，朋友送的但用不上。', '数码配件', 85.00, 1, 178, 15, 'https://picsum.photos/400/400?random=4', TRUE, '2025-11-10 16:45:00'),
(1, 'C语言程序设计（谭浩强）', 'C程序设计第五版，谭浩强编著。八成新，有笔记和课后习题答案标注。', '教科书', 28.00, 1, 67, 3, 'https://picsum.photos/400/400?random=5', TRUE, '2025-11-15 11:00:00');

-- 李四发布的商品（6件 - 毕业清仓）
INSERT INTO items (seller_id, title, description, category, price, stock, views, favorites, image_url, is_active, created_at) VALUES
(2, '宿舍书桌台灯', '飞利浦护眼台灯，三档亮度调节，USB供电。使用3年但功能正常，底座有轻微划痕。', '生活用品', 45.00, 1, 123, 6, 'https://picsum.photos/400/400?random=6', TRUE, '2025-11-03 13:30:00'),
(2, '宿舍床上书桌', '折叠式床上电脑桌，竹制，60*40cm，可调节高度和角度。毕业清仓，9成新。', '生活用品', 55.00, 1, 198, 9, 'https://picsum.photos/400/400?random=7', TRUE, '2025-11-04 10:20:00'),
(2, '毕业论文打印装订券（50份）', '学校打印店充值卡余额50份打印装订券，每份可打印装订一本毕业论文。转让价7折。', '其他', 350.00, 1, 45, 2, 'https://picsum.photos/400/400?random=8', TRUE, '2025-11-06 15:10:00'),
(2, '电吹风（大功率）', '飞科电吹风，2200W大功率，冷热风三档，负离子护发。使用2年，吹风口有点灰但清洗后完好。', '生活用品', 40.00, 1, 87, 4, 'https://picsum.photos/400/400?random=9', TRUE, '2025-11-08 09:50:00'),
(2, '四级英语词汇书', '新东方四级词汇乱序版，带MP3光盘。有划线和笔记，适合突击备考。', '教科书', 15.00, 2, 112, 7, 'https://picsum.photos/400/400?random=10', TRUE, '2025-11-12 14:00:00'),
(2, '机械制图模板套装', '机械制图专用模板尺套装（8件），包括圆模板、椭圆模板、螺母模板等。全新，专业课不考了用不上。', '学习用品', 25.00, 1, 56, 3, 'https://picsum.photos/400/400?random=11', TRUE, '2025-11-18 16:30:00');

-- 王五发布的商品（4件 - 健身和数码）
INSERT INTO items (seller_id, title, description, category, price, stock, views, favorites, image_url, is_active, created_at) VALUES
(3, '小米手环7 NFC版', '小米手环7 NFC版，支持门禁卡、交通卡模拟。使用半年，屏幕无划痕，附原装充电器和两条表带。', '数码配件', 120.00, 1, 289, 18, 'https://picsum.photos/400/400?random=12', TRUE, '2025-11-07 11:20:00'),
(3, '瑜伽垫（NBR加厚）', 'Keep联名款瑜伽垫，15mm加厚NBR材质，185*80cm。使用3个月，无破损，送绑带和背包。', '运动器材', 68.00, 1, 145, 11, 'https://picsum.photos/400/400?random=13', TRUE, '2025-11-09 10:15:00'),
(3, '哑铃套装（可调节20kg）', '快速调节哑铃套装，5-20kg分档可调，节省空间。买了很少用，9.5成新。校内自提。', '运动器材', 280.00, 1, 201, 14, 'https://picsum.photos/400/400?random=14', TRUE, '2025-11-13 15:40:00'),
(3, 'AirPods 2代', '苹果AirPods 第二代，H1芯片，使用1年半，电池健康度85%左右。附原装充电盒和数据线。', '数码配件', 380.00, 1, 456, 23, 'https://picsum.photos/400/400?random=15', TRUE, '2025-11-16 13:25:00');

-- 赵六发布的商品（3件 - 刚用不久又不需要了）
INSERT INTO items (seller_id, title, description, category, price, stock, views, favorites, image_url, is_active, created_at) VALUES
(4, '收纳箱3个装（大号）', '透明塑料收纳箱3个，60*40*35cm。搬宿舍时买的，后来发现空间够用就闲置了。', '生活用品', 60.00, 3, 78, 5, 'https://picsum.photos/400/400?random=16', TRUE, '2025-11-11 09:30:00'),
(4, '数据结构与算法（C语言版）', '数据结构（C语言版）严蔚敏著，计算机专业必修课教材。全新，课程改用Java版了。', '教科书', 35.00, 1, 134, 9, 'https://picsum.photos/400/400?random=17', TRUE, '2025-11-14 14:50:00'),
(4, 'U盘 128GB', '闪迪128GB USB3.1高速U盘，读取速度150MB/s。全新未拆封，抽奖抽到的重复了。', '数码配件', 55.00, 1, 167, 12, 'https://picsum.photos/400/400?random=18', TRUE, '2025-11-17 10:10:00');

-- =========================================
-- 4. 收藏记录（模拟用户浏览和收藏）
-- =========================================
INSERT INTO favorites (user_id, item_id, created_at) VALUES
-- 赵六收藏的（打算买教材和数码产品）
(4, 1, '2025-11-19 10:15:00'),  -- 高等数学
(4, 2, '2025-11-19 10:16:00'),  -- 线性代数
(4, 3, '2025-11-19 10:20:00'),  -- 小米鼠标
(4, 12, '2025-11-19 15:30:00'), -- 小米手环
-- 孙七收藏的（喜欢健身和生活用品）
(5, 6, '2025-11-20 09:00:00'),  -- 台灯
(5, 7, '2025-11-20 09:05:00'),  -- 床上书桌
(5, 13, '2025-11-20 14:20:00'), -- 瑜伽垫
(5, 14, '2025-11-20 14:25:00'), -- 哑铃
-- 张三收藏的（看看健身器材）
(1, 13, '2025-11-21 11:00:00'), -- 瑜伽垫
(1, 14, '2025-11-21 11:05:00'), -- 哑铃
-- 李四收藏的（打算买数码产品）
(2, 12, '2025-11-21 16:30:00'), -- 小米手环
(2, 15, '2025-11-21 16:35:00'), -- AirPods
(2, 18, '2025-11-21 16:40:00'); -- U盘

-- =========================================
-- 5. 创建订单（模拟真实交易）
-- =========================================

-- 订单1：赵六购买张三的高等数学教材
INSERT INTO orders (order_number, buyer_id, seller_id, total_amount, status, payment_method, address_id, shipping_address, created_at) VALUES
('ORD20251120001', 4, 1, 45.00, 'completed', 'alipay', 4, '江苏省南京市玄武区东南大学九龙湖校区 李园3舍210', '2025-11-20 10:30:00');

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(1, 1, 1, 45.00, '2025-11-20 10:30:00');

-- 更新库存
UPDATE items SET stock = stock - 1 WHERE id = 1;

-- 订单2：孙七购买李四的台灯和床上书桌
INSERT INTO orders (order_number, buyer_id, seller_id, total_amount, status, payment_method, address_id, shipping_address, created_at) VALUES
('ORD20251121001', 5, 2, 100.00, 'completed', 'wechat', 5, '江苏省南京市玄武区东南大学九龙湖校区 桂园6舍301', '2025-11-21 09:15:00');

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(2, 6, 1, 45.00, '2025-11-21 09:15:00'),
(2, 7, 1, 55.00, '2025-11-21 09:15:00');

-- 更新库存
UPDATE items SET stock = stock - 1 WHERE id = 6;
UPDATE items SET stock = stock - 1 WHERE id = 7;

-- 订单3：赵六购买张三的小米鼠标
INSERT INTO orders (order_number, buyer_id, seller_id, total_amount, status, payment_method, address_id, shipping_address, remarks, created_at) VALUES
('ORD20251122001', 4, 1, 35.00, 'completed', 'alipay', 4, '江苏省南京市玄武区东南大学九龙湖校区 李园3舍210', '请帮我测试一下鼠标是否正常', '2025-11-22 14:20:00');

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(3, 3, 1, 35.00, '2025-11-22 14:20:00');

-- 更新库存
UPDATE items SET stock = stock - 1 WHERE id = 3;

-- 订单4：张三购买王五的瑜伽垫
INSERT INTO orders (order_number, buyer_id, seller_id, total_amount, status, payment_method, address_id, shipping_address, created_at) VALUES
('ORD20251123001', 1, 3, 68.00, 'shipped', 'alipay', 1, '江苏省南京市玄武区东南大学九龙湖校区 橘园5舍201', '2025-11-23 11:00:00');

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(4, 13, 1, 68.00, '2025-11-23 11:00:00');

-- 更新库存
UPDATE items SET stock = stock - 1 WHERE id = 13;

-- 订单5：李四购买王五的小米手环（待支付）
INSERT INTO orders (order_number, buyer_id, seller_id, total_amount, status, payment_method, address_id, shipping_address, created_at) VALUES
('ORD20251124001', 2, 3, 120.00, 'pending', 'alipay', 2, '江苏省南京市玄武区东南大学九龙湖校区 梅园2舍305', '2025-11-24 15:30:00');

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(5, 12, 1, 120.00, '2025-11-24 15:30:00');

-- 订单6：孙七购买李四的四级词汇书2本
INSERT INTO orders (order_number, buyer_id, seller_id, total_amount, status, payment_method, address_id, shipping_address, created_at) VALUES
('ORD20251125001', 5, 2, 30.00, 'completed', 'wechat', 5, '江苏省南京市玄武区东南大学九龙湖校区 桂园6舍301', '2025-11-25 10:00:00');

INSERT INTO order_items (order_id, item_id, quantity, unit_price, created_at) VALUES
(6, 10, 2, 15.00, '2025-11-25 10:00:00');

-- 更新库存
UPDATE items SET stock = stock - 2 WHERE id = 10;

-- =========================================
-- 6. 添加评价（已完成的订单）
-- =========================================

-- 赵六评价订单1（高等数学教材）
INSERT INTO reviews (order_id, reviewer_id, reviewee_id, item_id, rating, comment, created_at) VALUES
(1, 4, 1, 1, 5, '书的质量很好，笔记也很有用，卖家很耐心地解答我的问题。强烈推荐！', '2025-11-21 20:15:00');

-- 孙七评价订单2（台灯和床上书桌）
INSERT INTO reviews (order_id, reviewer_id, reviewee_id, rating, comment, created_at) VALUES
(2, 5, 2, 4, '东西都不错，台灯虽然有点旧但完全能用，床上桌子很实用。卖家人很好，还帮我送到宿舍楼下。', '2025-11-22 18:30:00');

-- 赵六评价订单3（小米鼠标）
INSERT INTO reviews (order_id, reviewer_id, reviewee_id, item_id, rating, comment, created_at) VALUES
(3, 4, 1, 3, 5, '鼠标功能完好，蓝牙和2.4G都能正常使用。卖家交易前还特地帮我测试了，非常负责！', '2025-11-23 09:00:00');

-- 孙七评价订单6（四级词汇书）
INSERT INTO reviews (order_id, reviewer_id, reviewee_id, rating, comment, created_at) VALUES
(6, 5, 2, 5, '词汇书质量不错，笔记标注对复习很有帮助。价格实惠，好评！', '2025-11-26 14:20:00');

-- =========================================
-- 7. 更新商品浏览量（模拟真实浏览）
-- =========================================
UPDATE items SET views = views + FLOOR(RAND() * 50) + 10;

-- =========================================
-- 测试数据插入完成
-- =========================================

SELECT '========================================' AS '';
SELECT '测试数据插入完成！' AS '状态';
SELECT '========================================' AS '';

-- 显示统计信息
SELECT 
    '用户' AS '类型',
    COUNT(*) AS '数量'
FROM users
UNION ALL
SELECT '商品', COUNT(*) FROM items
UNION ALL
SELECT '在售商品', COUNT(*) FROM items WHERE is_active = TRUE AND stock > 0
UNION ALL
SELECT '收藏记录', COUNT(*) FROM favorites
UNION ALL
SELECT '地址', COUNT(*) FROM addresses
UNION ALL
SELECT '订单', COUNT(*) FROM orders
UNION ALL
SELECT '已完成订单', COUNT(*) FROM orders WHERE status = 'completed'
UNION ALL
SELECT '待支付订单', COUNT(*) FROM orders WHERE status = 'pending'
UNION ALL
SELECT '评价', COUNT(*) FROM reviews;

-- 显示商品库存状态
SELECT 
    '===== 商品库存状态 =====' AS '';
SELECT 
    title AS '商品名称',
    stock AS '剩余库存',
    views AS '浏览量',
    favorites AS '收藏数',
    CASE 
        WHEN stock = 0 THEN '已售罄'
        WHEN stock <= 2 THEN '库存紧张'
        ELSE '库存充足'
    END AS '状态'
FROM items
WHERE is_active = TRUE
ORDER BY stock ASC, views DESC;
