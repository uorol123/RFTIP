"""
服务初始化脚本
用于初始化 MySQL 数据库、MinIO 存储桶等
"""
import sys
import re
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import (
    DATABASE_URL,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)


# ==================== MySQL 初始化 ====================

def init_mysql():
    """初始化 MySQL 数据库和表"""
    print("\n" + "=" * 50)
    print("初始化 MySQL 数据库")
    print("=" * 50)

    try:
        import pymysql
        from sqlalchemy import create_engine, inspect
        from core.database import Base

        # 导入所有模型
        from app.models import User, UserLoginLog, DataFile
        from app.models import RadarStation, FlightTrackRaw, FlightTrackCorrected
        from app.models import RestrictedZone, ZoneIntrusion

    except ImportError as e:
        print(f"[ERROR] 缺少必要的模块: {e}")
        return False

    # 解析 DATABASE_URL
    # 格式: mysql+pymysql://root:password@localhost:3306/rftip
    pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, DATABASE_URL)

    if not match:
        print(f"[ERROR] 无法解析 DATABASE_URL: {DATABASE_URL}")
        return False

    username, password, host, port, database = match.groups()

    print(f"主机: {host}:{port}")
    print(f"数据库: {database}")

    try:
        # 1. 创建数据库（如果不存在）
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        cursor.execute(f"SHOW DATABASES LIKE '{database}'")
        result = cursor.fetchone()

        if result:
            print(f"[OK] 数据库 '{database}' 已存在")
        else:
            cursor.execute(f"""
                CREATE DATABASE `{database}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
            """)
            print(f"[OK] 数据库 '{database}' 创建成功")

        cursor.close()
        connection.close()

        # 2. 创建数据表
        print("\n开始创建数据表...")
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)

        # 显示创建的表
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"[OK] 数据表创建成功 ({len(tables)} 个表):")
        for table in tables:
            print(f"  - {table}")

        engine.dispose()
        return True

    except Exception as e:
        print(f"[ERROR] MySQL 初始化失败: {e}")
        return False


# ==================== MinIO 初始化 ====================

def init_minio():
    """初始化 MinIO 存储桶"""
    print("\n" + "=" * 50)
    print("初始化 MinIO 存储")
    print("=" * 50)

    if not MINIO_ENDPOINT:
        print("[SKIP] MINIO_ENDPOINT 未配置，跳过 MinIO 初始化")
        return True

    try:
        from minio import Minio

        print(f"MinIO 端点: {MINIO_ENDPOINT}")
        print(f"存储桶: {MINIO_BUCKET}")

        # 创建 MinIO 客户端
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )

        # 检查并创建存储桶
        if client.bucket_exists(MINIO_BUCKET):
            print(f"[OK] 存储桶 '{MINIO_BUCKET}' 已存在")
        else:
            client.make_bucket(MINIO_BUCKET)
            print(f"[OK] 存储桶 '{MINIO_BUCKET}' 创建成功")

        return True

    except ImportError:
        print("[WARN] 缺少 minio 模块，跳过 MinIO 初始化")
        return True
    except Exception as e:
        print(f"[ERROR] MinIO 初始化失败: {e}")
        return False


# ==================== Redis 检查 ====================

def check_redis():
    """检查 Redis 连接"""
    print("\n" + "=" * 50)
    print("检查 Redis 连接")
    print("=" * 50)

    try:
        import redis
        from core.config import REDIS_URL

        print(f"Redis URL: {REDIS_URL}")

        client = redis.from_url(REDIS_URL, socket_connect_timeout=5)
        client.ping()
        print("[OK] Redis 连接正常")
        client.close()
        return True

    except ImportError:
        print("[WARN] 缺少 redis 模块，跳过 Redis 检查")
        return True
    except Exception as e:
        print(f"[WARN] Redis 连接失败: {e}")
        return True  # Redis 不阻塞初始化


# ==================== 目录初始化 ====================

def init_directories():
    """创建必要的目录"""
    print("\n" + "=" * 50)
    print("初始化目录结构")
    print("=" * 50)

    directories = [
        "logs",          # 日志目录
        "uploads",       # 上传文件临时目录
        "exports",       # 导出文件目录
    ]

    for dir_name in directories:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] 创建目录: {dir_name}")
        else:
            print(f"[OK] 目录已存在: {dir_name}")

    return True


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 50)
    print("RFTIP 服务初始化")
    print("=" * 50)
    print(f"项目路径: {project_root}")

    results = {}

    # 1. 初始化目录
    results["目录"] = init_directories()

    # 2. 初始化 MySQL
    results["MySQL"] = init_mysql()

    # 3. 检查 Redis
    results["Redis"] = check_redis()

    # 4. 初始化 MinIO
    results["MinIO"] = init_minio()

    # 汇总结果
    print("\n" + "=" * 50)
    print("初始化结果汇总")
    print("=" * 50)

    for service, success in results.items():
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{service}: {status}")

    all_success = all(results.values())

    print("=" * 50)
    if all_success:
        print("[OK] 所有服务初始化成功！")
    else:
        print("[WARN] 部分服务初始化失败，请检查配置")
    print("=" * 50)

    return 0 if all_success else 1


if __name__ == "__main__":
    exit(main())
