-- 查看当前数据库状态
USE seu_second_hand;

SELECT '===== 数据库表统计 =====' AS '';
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
SELECT '评价', COUNT(*) FROM reviews;

SELECT '=====' AS '';
SELECT '===== 商品列表 =====' AS '';
SELECT 
    id AS 'ID',
    title AS '商品名称',
    category AS '分类',
    price AS '价格',
    stock AS '库存',
    views AS '浏览',
    favorites AS '收藏',
    is_active AS '在售'
FROM items
ORDER BY id;

SELECT '=====' AS '';
SELECT '===== 订单列表 =====' AS '';
SELECT 
    o.id AS 'ID',
    o.order_number AS '订单号',
    u1.username AS '买家',
    u2.username AS '卖家',
    o.total_amount AS '金额',
    o.status AS '状态'
FROM orders o
LEFT JOIN users u1 ON o.buyer_id = u1.id
LEFT JOIN users u2 ON o.seller_id = u2.id;
