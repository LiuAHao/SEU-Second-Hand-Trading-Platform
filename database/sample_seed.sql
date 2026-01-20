-- 开发演示用初始化数据（MySQL 8+）
-- 使用前请先修改 USE 语句为实际数据库名
USE seu_second_hand;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 清空旧数据（谨慎执行）
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE favorites;
TRUNCATE TABLE items;
TRUNCATE TABLE addresses;
TRUNCATE TABLE users;

-- 统一密码哈希（明文：Password123）
SET @pw := '$2b$12$KIXx1YF8q9H5uzRJpc6G8eGkZZgwyXR0YJIUKGwEuKXXSb9ECf66K';

INSERT INTO users (id, username, password_hash, email, phone, avatar_url, bio, created_at, updated_at, is_active) VALUES
  (1, 'alice', @pw, 'alice@seu.edu.cn', '13800000001', NULL, '爱读书的理科生', NOW(), NOW(), 1),
  (2, 'bob',   @pw, 'bob@seu.edu.cn',   '13800000002', NULL, '运动爱好者',     NOW(), NOW(), 1),
  (3, 'carol', @pw, 'carol@seu.edu.cn', '13800000003', NULL, '数码重度用户',   NOW(), NOW(), 1),
  (4, 'dave',  @pw, 'dave@seu.edu.cn',  '13800000004', NULL, '宿舍生活达人',   NOW(), NOW(), 1);

INSERT INTO addresses (id, user_id, recipient_name, phone, province, city, district, detail, is_default, created_at, updated_at) VALUES
  (1, 1, 'Alice', '13800000001', '江苏省', '南京市', '九龙湖校区', '南园 5 栋 302', 1, NOW(), NOW()),
  (2, 2, 'Bob',   '13800000002', '江苏省', '南京市', '四牌楼校区', '东区 12 栋 218', 1, NOW(), NOW()),
  (3, 3, 'Carol', '13800000003', '江苏省', '南京市', '丁家桥校区', '科研楼 3 楼 305', 1, NOW(), NOW()),
  (4, 4, 'Dave',  '13800000004', '江苏省', '南京市', '九龙湖校区', '学生公寓 9 栋 101',1, NOW(), NOW());

INSERT INTO items (id, seller_id, title, description, category, price, stock, views, favorites, image_url, created_at, updated_at, is_active) VALUES
  (1, 1, '高数第七版（上）', '附课堂笔记，书脊完好', 'books', 25.00, 10, 5, 1, NULL, NOW(), NOW(), 1),
  (2, 1, '线性代数教材', '含重点标注与思维导图', 'books', 30.00, 8, 3, 0, NULL, NOW(), NOW(), 1),
  (3, 2, '羽毛球拍+拍包', '入门碳素拍，送3只球', 'sports', 120.00, 5, 2, 0, NULL, NOW(), NOW(), 1),
  (4, 2, 'NIKE 篮球鞋 42码', '室内木地板使用，九成新', 'sports', 360.00, 3, 6, 1, NULL, NOW(), NOW(), 1),
  (5, 3, 'iPad Air 4 64G', '深空灰，轻微划痕，含原装壳', 'electronics', 2600.00, 2, 12, 2, NULL, NOW(), NOW(), 1),
  (6, 3, 'Kindle Paperwhite 11', '8G 带保护壳，电池健康', 'electronics', 520.00, 6, 7, 1, NULL, NOW(), NOW(), 1),
  (7, 3, '27寸 2K 显示器', 'IPS 75Hz，无亮点，附HDMI线', 'electronics', 680.00, 4, 4, 0, NULL, NOW(), NOW(), 1),
  (8, 4, '宿舍小冰箱 90L', '静音省电，支持校内自提', 'daily', 480.00, 2, 9, 1, NULL, NOW(), NOW(), 1),
  (9, 4, '收纳抽屉柜', '四层塑料柜，稳固无异味', 'daily', 90.00, 8, 1, 0, NULL, NOW(), NOW(), 1),
  (10,4, 'Type-C 65W 插排', '6位插孔+2C1A，带过载保护', 'other', 110.00, 9, 2, 0, NULL, NOW(), NOW(), 1);

-- 示例订单（买家=Alice，卖家=Carol，地址=1）
INSERT INTO orders (id, order_number, buyer_id, seller_id, address_id, total_amount, status, remarks, shipping_address, created_at, updated_at) VALUES
  (1, 'ORD202601200001', 1, 3, 1, 2600.00, 'paid', '请周末送达', '江苏省 南京市 九龙湖校区 南园 5 栋 302', NOW(), NOW());

INSERT INTO order_items (id, order_id, item_id, quantity, unit_price, created_at) VALUES
  (1, 1, 5, 1, 2600.00, NOW());

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;
