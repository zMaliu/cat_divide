# 🐱 云护萌 - 广工数院本科生创新项目

## 项目概述

**云护萌**是广东工业大学数学与统计学院本科生创新项目，旨在通过技术手段实现对猫咪相关信息的数字化管理与智能识别，提升校园流浪猫管理效率与公众参与度。

## 环境依赖

### 必需软件

- **Python 3.8+**
- **Docker Desktop**（用于 Milvus 向量数据库）
- **MySQL 8.0+**（或 MariaDB）
- **微信开发者工具**

## 快速启动

### 1. 安装依赖

```
pip install -r 后端/requirements.txt
```

### 2. 配置环境变量

在后端根目录下创建 `.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=cat

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# 安全配置
SECRET_KEY=your_secret_key_here

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530
VECTOR_COLLECTION_NAME=cat_vectors
```

### 3. 初始化数据库

执行 `数据库/cat.sql` 脚本创建数据库表结构：

```sql
-- 创建数据库
CREATE DATABASE cat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE cat;

-- 执行 cat.sql 中的所有建表语句
```

### 4. 启动服务

#### 步骤 1：启动 Milvus 向量数据库

```bash
# 使用命令行
docker compose -p catdivide-milvus up -d
```

等待约 1-2 分钟，直到 Milvus 服务完全启动（可通过 `http://localhost:9091/healthz` 验证）。

#### 步骤 2：启动 Flask 应用

```bash
cd 后端
python main.py
```

应用将在 `http://127.0.0.1:5001` 运行
