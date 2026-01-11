# 快速启动指南

适用：Python 3.10+、MySQL 8.0+、Windows/macOS/Linux。

## 步骤
1) 克隆项目
```bash
git clone <repo-url>
cd SEU-Second-Hand-Trading-Platform
```

2) 安装依赖
```bash
pip install -r requirements.txt
```

3) 创建数据库（utf8mb4）
```bash
mysql -u root -p -e "CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

4) 导入结构（使用最新版 schema_optimized.sql）
```bash
mysql -u root -p seu_second_hand < database/schema_optimized.sql
```

（旧版库如需迁移，可执行）
```bash
mysql -u root -p seu_second_hand < database/migration_v1_to_v2_fixed.sql
```

5) 可选：导入示例数据
```bash
mysql -u root -p seu_second_hand < database/seed_data.sql
```

6) 启动应用
```bash
python run.py  # http://localhost:5000
```

## 环境变量
复制 .env.example 为 .env，至少设置：
- DATABASE_URI=mysql+pymysql://user:password@localhost:3306/seu_second_hand?charset=utf8mb4
- SECRET_KEY=
- JWT_SECRET_KEY=

## 常用命令
- 迁移旧库：mysql -u root -p seu_second_hand < database/migration_v1_to_v2_fixed.sql
- 查看表：mysql -u root -p seu_second_hand -e "SHOW TABLES;"

