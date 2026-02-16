"""
服务连接测试脚本
验证 MySQL、Redis、MinIO 的连接状态
"""
import sys
import re
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import (
    DATABASE_URL,
    REDIS_URL,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)


def test_mysql_connection():
    """测试 MySQL 数据库连接"""
    print("\n" + "=" * 50)
    print("测试 MySQL 连接")
    print("=" * 50)

    db_url = DATABASE_URL

    if not db_url:
        print("[ERROR] DATABASE_URL 未配置，请在 .env 文件中设置")
        return False

    try:
        import pymysql

        # 解析 DATABASE_URL
        # 格式: mysql+pymysql://root:password@localhost:3306/rftip
        pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, db_url)

        if not match:
            print(f"[ERROR] 无法解析 DATABASE_URL: {db_url}")
            return False

        username, password, host, port, database = match.groups()

        print(f"主机: {host}:{port}")
        print(f"数据库: {database}")
        print(f"用户: {username}")

        # 连接数据库
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=5
        )

        # 执行简单查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]

        connection.close()

        print(f"[OK] MySQL 连接成功")
        print(f"[INFO] MySQL 版本: {version}")
        print(f"[INFO] 可用数据库: {', '.join(databases[:5])}...")
        return True

    except ImportError:
        print("[ERROR] 缺少 pymysql 模块，请执行: pip install pymysql")
        return False
    except Exception as e:
        print(f"[ERROR] MySQL 连接失败: {e}")
        return False


def test_redis_connection():
    """测试 Redis 连接"""
    print("\n" + "=" * 50)
    print("测试 Redis 连接")
    print("=" * 50)

    redis_url = REDIS_URL

    if not redis_url:
        print("[ERROR] REDIS_URL 未配置，请在 .env 文件中设置")
        return False

    try:
        import redis

        print(f"Redis URL: {redis_url}")

        # 解析 Redis URL
        # 格式: redis://localhost:6379 或 redis://username:password@localhost:6379/0
        client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)

        # 测试连接
        ping_result = client.ping()
        info = client.info()

        print(f"[OK] Redis 连接成功")
        print(f"[INFO] Redis 版本: {info.get('redis_version', 'unknown')}")
        print(f"[INFO] 运行模式: {'集群' if info.get('role') == 'master' else '单机'}")

        client.close()
        return True

    except ImportError:
        print("[ERROR] 缺少 redis 模块，请执行: pip install redis")
        return False
    except Exception as e:
        print(f"[ERROR] Redis 连接失败: {e}")
        return False


def test_minio_connection():
    """测试 MinIO 连接"""
    print("\n" + "=" * 50)
    print("测试 MinIO 连接")
    print("=" * 50)

    endpoint = MINIO_ENDPOINT
    access_key = MINIO_ACCESS_KEY
    secret_key = MINIO_SECRET_KEY
    bucket_name = MINIO_BUCKET
    secure = MINIO_SECURE

    if not endpoint:
        print("[ERROR] MINIO_ENDPOINT 未配置，请在 .env 文件中设置")
        return False
    if not access_key:
        print("[ERROR] MINIO_ACCESS_KEY 未配置，请在 .env 文件中设置")
        return False
    if not secret_key:
        print("[ERROR] MINIO_SECRET_KEY 未配置，请在 .env 文件中设置")
        return False

    try:
        from minio import Minio

        print(f"MinIO 端点: {endpoint}")
        print(f"Access Key: {access_key[:4]}****")
        print(f"Bucket: {bucket_name}")
        print(f"安全连接: {secure}")

        # 创建 MinIO 客户端
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

        # 测试连接 - 获取存储桶列表
        buckets = client.list_buckets()
        bucket_names = [b.name for b in buckets]

        # 检查指定 bucket 是否存在
        bucket_exists = client.bucket_exists(bucket_name)

        print(f"[OK] MinIO 连接成功")
        print(f"[INFO] 可用存储桶: {', '.join(bucket_names) if bucket_names else '无'}")
        print(f"[INFO] 存储桶 '{bucket_name}': {'存在' if bucket_exists else '不存在'}")

        return True

    except ImportError:
        print("[ERROR] 缺少 minio 模块，请执行: pip install minio")
        return False
    except Exception as e:
        print(f"[ERROR] MinIO 连接失败: {e}")
        return False


def main():
    """主函数 - 运行所有连接测试"""
    print("=" * 50)
    print("RFTIP 服务连接测试")
    print("=" * 50)
    print(f"项目路径: {project_root}")

    results = {
        "MySQL": test_mysql_connection(),
        "Redis": test_redis_connection(),
        "MinIO": test_minio_connection()
    }

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for service, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{service}: {status}")

    all_passed = all(results.values())

    print("=" * 50)
    if all_passed:
        print("[OK] 所有服务连接正常")
    else:
        print("[WARN] 部分服务连接失败，请检查配置")
    print("=" * 50)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
