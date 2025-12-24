-- 东南大学校园二手交易平台 - 测试数据
-- 创建测试用户、商品、订单等数据

-- =========================================
-- 测试用户数据（密码：bcrypt哈希）
-- 实际密码都是：Password123
-- =========================================

INSERT INTO users (username, email, password_hash, phone, bio, is_active) VALUES
('zhangsan', 'zhangsan@seu.edu.cn', '$2b$12$KIX9Q2hNLV9Y5Y3Y.9Y5e.mFx5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y', '13800138001', '二手书专业卖家，诚信交易', TRUE),
('lisi', 'lisi@seu.edu.cn', '$2b$12$KIX9Q2hNLV9Y5Y3Y.9Y5e.mFx5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y', '13800138002', '学生，爱好电子产品', TRUE),
('wangwu', 'wangwu@seu.edu.cn', '$2b$12$KIX9Q2hNLV9Y5Y3Y.9Y5e.mFx5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y', '13800138003', '运动爱好者', TRUE),
('zhaoliu', 'zhaoliu@seu.edu.cn', '$2b$12$KIX9Q2hNLV9Y5Y3Y.9Y5e.mFx5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y', '13800138004', '生活用品清仓', TRUE),
('admin', 'admin@seu.edu.cn', '$2b$12$KIX9Q2hNLV9Y5Y3Y.9Y5e.mFx5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y', '13800138000', '平台管理员', TRUE);


-- =========================================
-- 测试商品数据
-- =========================================

-- 教材书籍分类
INSERT INTO items (seller_id, title, description, category, price, stock, views, image_url, is_active) VALUES
(1, '高等数学教材 2024年版', '高等数学（上下册）原版，笔记较少，品相较新，共2册', 'books', 45.00, 3, 125, 'https://via.placeholder.com/300x300?text=高等数学', TRUE),
(1, '线性代数习题集', '线性代数习题集，有手写笔记，答题比例70%，适合复习', 'books', 25.00, 2, 89, 'https://via.placeholder.com/300x300?text=线性代数', TRUE),
(2, '概率论与数理统计', '2023年新版，全新，未使用，原价89元，现售70元', 'books', 70.00, 1, 56, 'https://via.placeholder.com/300x300?text=概率论', TRUE),
(1, '大学英语教材全套', '大学英语综合教程1-4册，品相完好，送2024年词汇表', 'books', 80.00, 2, 145, 'https://via.placeholder.com/300x300?text=大学英语', TRUE),

-- 电子产品分类
INSERT INTO items (seller_id, title, description, category, price, stock, views, image_url, is_active) VALUES
(2, '小米台灯 Pro', '小米台灯Pro，使用3个月，外观完好，支持亮度调节，国行正品', 'electronics', 120.00, 1, 234, 'https://via.placeholder.com/300x300?text=小米台灯', TRUE),
(3, 'iPad Air 2024款 64GB', '苹果iPad Air 256GB，2024年款，已激活但使用不足2周，附原装配件', 'electronics', 3200.00, 1, 567, 'https://via.placeholder.com/300x300?text=iPad', TRUE),
(2, '骨传导耳机 开源版', '开源骨传导耳机，蓝牙5.3，续航8小时，防水等级IP67', 'electronics', 280.00, 2, 178, 'https://via.placeholder.com/300x300?text=骨传导耳机', TRUE),
(4, '充电器套装（5件）', '各种规格USB-C充电器5个，全新未使用，包括18W/25W/45W/65W快充', 'electronics', 50.00, 5, 92, 'https://via.placeholder.com/300x300?text=充电器', TRUE),

-- 生活用品分类
INSERT INTO items (seller_id, title, description, category, price, stock, views, image_url, is_active) VALUES
(4, '宿舍神器套装', '包含：台灯+风扇+加热水杯，全新，原价299元，现售150元', 'daily', 150.00, 2, 201, 'https://via.placeholder.com/300x300?text=宿舍神器', TRUE),
(3, '双层宿舍床垫', '学生用双层床垫，海绵材质，厚8cm，适合1米宽床位，使用1个学期', 'daily', 80.00, 1, 145, 'https://via.placeholder.com/300x300?text=床垫', TRUE),
(1, '收纳柜 三层', '塑料收纳柜，三层设计，尺寸60*40*90cm，完好无损，送安装', 'daily', 120.00, 3, 167, 'https://via.placeholder.com/300x300?text=收纳柜', TRUE),
(2, '隐形窗帘杆', '北欧风隐形窗帘杆，装修时购买多了，全新未使用，长2米', 'daily', 60.00, 2, 78, 'https://via.placeholder.com/300x300?text=窗帘杆', TRUE),

-- 运动器材分类
INSERT INTO items (seller_id, title, description, category, price, stock, views, image_url, is_active) VALUES
(3, '瑜伽垫 TPE材质', '瑜伽垫TPE材质，厚8mm，防滑耐用，配背包，使用2个月', 'sports', 45.00, 2, 112, 'https://via.placeholder.com/300x300?text=瑜伽垫', TRUE),
(1, '哑铃片套装 20kg', '家用哑铃片组合，共20kg，包括哑铃杆2根，二手但无损伤', 'sports', 180.00, 1, 234, 'https://via.placeholder.com/300x300?text=哑铃', TRUE),
(3, '跳绳 速度训练款', '高速钢丝跳绳，调节长度，适合速度训练和有氧运动，全新', 'sports', 35.00, 5, 89, 'https://via.placeholder.com/300x300?text=跳绳', TRUE),
(4, '瑜伽球 65cm', '瑜伽球65cm，PVC材质，充气使用2个月，送气泵', 'sports', 50.00, 1, 67, 'https://via.placeholder.com/300x300?text=瑜伽球', TRUE);


-- =========================================
-- 测试配送地址数据
-- =========================================

INSERT INTO addresses (user_id, recipient_name, phone, province, city, district, detail, is_default) VALUES
(1, '张三', '13800138001', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 A区宿舍203', TRUE),
(1, '张三', '13800138001', '江苏省', '常州市', '天宁区', '常州市天宁区中山路123号', FALSE),
(2, '李四', '13800138002', '江苏省', '南京市', '鼓楼区', '东南大学四牌楼校区 电子楼', FALSE),
(2, '李四父亲', '13800138005', '江苏省', '南京市', '江宁区', '江宁区学府路888号', TRUE),
(3, '王五', '13800138003', '江苏省', '南京市', '玄武区', '东南大学九龙湖校区 中心食堂', TRUE),
(4, '赵六', '13800138004', '江苏省', '南京市', '栖霞区', '东南大学丁家桥校区 学生公寓2号楼', FALSE);


-- =========================================
-- 测试订单数据
-- =========================================

-- 订单1：购买教材和书籍
INSERT INTO orders (buyer_id, total_amount, status, shipping_address, created_at) VALUES
(2, 95.00, 'completed', '东南大学四牌楼校区 电子楼', '2024-12-20 10:30:00');

INSERT INTO order_items (order_id, item_id, quantity, price_at_purchase) VALUES
(1, 1, 1, 45.00),
(1, 2, 1, 25.00),
(1, 3, 1, 70.00);

-- 订单2：购买电子产品
INSERT INTO orders (buyer_id, total_amount, status, shipping_address, created_at) VALUES
(3, 280.00, 'pending', '东南大学九龙湖校区 中心食堂', '2024-12-22 14:50:00');

INSERT INTO order_items (order_id, item_id, quantity, price_at_purchase) VALUES
(2, 9, 1, 280.00);

-- 订单3：购买生活用品
INSERT INTO orders (buyer_id, total_amount, status, shipping_address, created_at) VALUES
(4, 230.00, 'shipped', '东南大学丁家桥校区 学生公寓2号楼', '2024-12-21 16:20:00');

INSERT INTO order_items (order_id, item_id, quantity, price_at_purchase) VALUES
(3, 13, 1, 150.00),
(3, 15, 1, 80.00);

-- 订单4：单件商品
INSERT INTO orders (buyer_id, total_amount, status, shipping_address, created_at) VALUES
(1, 45.00, 'completed', '东南大学九龙湖校区 A区宿舍203', '2024-12-19 09:15:00');

INSERT INTO order_items (order_id, item_id, quantity, price_at_purchase) VALUES
(4, 17, 1, 45.00);


-- =========================================
-- 测试评价数据（可选）
-- =========================================

INSERT INTO reviews (order_id, item_id, reviewer_id, reviewee_id, rating, content, created_at) VALUES
(1, 1, 2, 1, 5, '卖家服务超好，书籍品相完好，快递快，推荐！', '2024-12-21 10:00:00'),
(1, 2, 2, 1, 5, '习题集质量不错，笔记清楚，很有参考价值', '2024-12-21 10:05:00'),
(4, 17, 1, 3, 4, '宝贝品相很好，就是颜色和图片有点差异，但是能接受', '2024-12-20 15:30:00');


-- =========================================
-- 查询统计（用于验证数据）
-- =========================================

-- 统计用户数
SELECT COUNT(*) as 用户总数 FROM users;

-- 统计商品数及库存
SELECT COUNT(*) as 商品总数, SUM(stock) as 总库存 FROM items WHERE is_active = TRUE;

-- 统计订单及金额
SELECT COUNT(*) as 订单总数, SUM(total_amount) as 成交总额 FROM orders;

-- 各分类商品统计
SELECT category, COUNT(*) as 商品数, AVG(price) as 平均价格, SUM(stock) as 总库存
FROM items WHERE is_active = TRUE
GROUP BY category
ORDER BY 商品数 DESC;

-- 卖家销售统计
SELECT u.username, u.email, COUNT(DISTINCT o.id) as 订单数, SUM(o.total_amount) as 销售额
FROM users u
LEFT JOIN items i ON u.id = i.seller_id
LEFT JOIN order_items oi ON i.id = oi.item_id
LEFT JOIN orders o ON oi.order_id = o.id
WHERE o.id IS NOT NULL
GROUP BY u.id
ORDER BY 销售额 DESC;