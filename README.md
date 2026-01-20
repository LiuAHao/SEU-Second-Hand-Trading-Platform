# 东南大学校园二手交易平台

基于 Flask + MySQL 的校园内二手交易系统，支持发布、搜索、购物车、订单、评价、收货地址等完整流程。

## 核心功能
- 用户：校园邮箱登录、资料与信誉分。
- 商品：发布/搜索/分类、库存管理、图片上传。
- 订单：购物车、下单/取消、地址选择、状态流转。
- 评价：订单完成后评价与评分。

## 技术栈
- 后端：Flask 3.x、SQLAlchemy 2.x、JWT 认证、bcrypt。
- 前端：HTML/CSS/JS (ES6)，内置 API 客户端与 Mock 支持。
- 数据库：MySQL 8.0+，字符集 utf8mb4。

## 快速开始
1. 克隆并安装依赖
```bash
git clone <repo-url>
cd SEU-Second-Hand-Trading-Platform
pip install -r requirements.txt
```
2. 初始化数据库
```bash
mysql -u root -p -e "CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql --default-character-set=utf8mb4 -u root -p seu_second_hand < database/schema_optimized.sql
```
（可选）导入示例数据：`mysql --default-character-set=utf8mb4 -u root -p seu_second_hand < database/sample_seed.sql`
（旧库迁移）执行：`mysql --default-character-set=utf8mb4 -u root -p seu_second_hand < database/migration_v1_to_v2_fixed.sql`

3. 配置环境变量
创建 .env，设置 DATABASE_URI/SECRET_KEY/JWT_SECRET_KEY。

4. 启动
```bash
python run.py  # http://localhost:5000
```

更多细节见 [QUICK_START.md](QUICK_START.md)。

## 目录速览
```
app/        # 核心代码：api、services、models、templates、static
database/   # schema_optimized.sql、迁移与示例数据
tests/      # 单元与集成测试
```

## 文档
- API 规范：FRONTEND_API_DOCS.md
- 快速启动：QUICK_START.md
- AI 协作指南：CLAUDE.md

