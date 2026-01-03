# 快速启动指南

东南大学校园二手交易平台 - 本地开发环境配置

## 环境要求

- Python 3.10+
- MySQL 8.0+
- Windows PowerShell 或 Bash

## 一、克隆项目

```bash
git clone <repo-url>
cd SEU-Second-Hand-Trading-Platform
```

## 二、安装 Python 依赖

```powershell
pip install -r requirements.txt
```

**依赖包括：**
- Flask 3.0.3（Web框架）
- Flask-SQLAlchemy 3.1.1（ORM）
- PyMySQL 1.1.0（MySQL 驱动）
- bcrypt（密码加密）
- pytest 9.0.2（测试框架）

## 三、配置数据库

### 1. 启动 MySQL 服务

确保 MySQL 已安装并运行：
```powershell
# Windows 检查 MySQL 是否运行
Get-Service | Where-Object {$_.Name -like "*MySQL*"}
```

### 2. 创建数据库

在 PowerShell 中执行：

```powershell
# 连接到 MySQL
mysql -u root -p123456         #密码123456不成功时请尝试root

# 在 MySQL 命令行中创建数据库
mysql> CREATE DATABASE seu_second_hand CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
mysql> exit;
```

### 3. 导入数据库结构

回到 PowerShell：

```powershell
# 从项目根目录执行
Get-Content -Encoding UTF8 "database/schema_no_comment.sql" | mysql -u root -p123456 seu_second_hand
```

验证导入成功：

```powershell
mysql -u root -p123456 seu_second_hand -e "SHOW TABLES;"
```

应该看到 6 个表：
```
addresses, items, order_items, orders, reviews, users
```

## 四、启动应用

```powershell
python run.py
```

应该看到输出：
```
路由注册成功！
 * Running on http://127.0.0.1:5000
```

访问 http://localhost:5000 打开应用。

## 数据库配置

- **用户名：** root
- **密码：** root(本来是123456，实际使用发现123456不成功，请使用root)
- **主机：** localhost
- **端口：** 3306
- **数据库：** seu_second_hand

