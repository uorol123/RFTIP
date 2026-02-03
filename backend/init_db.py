"""
数据库初始化脚本
用于创建数据库和所有表
"""
import pymysql
from sqlalchemy import create_engine, text
from core.database import Base
from core.config import get_settings

# 导入所有模型，确保 SQLAlchemy 能够识别所有表
from app.models import User, UserLoginLog, DataFile
from app.models import RadarStation, FlightTrackRaw, FlightTrackCorrected
from app.models import RestrictedZone, ZoneIntrusion

settings = get_settings()


def create_database():
    """创建数据库"""
    # 从 DATABASE_URL 中解析连接信息
    # 格式: mysql+pymysql://root:password@localhost:3306/rftip
    db_url = settings.database_url
    # 提取用户名、密码、主机、端口、数据库名
    import re
    pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, db_url)

    if not match:
        print(f"无法解析 DATABASE_URL: {db_url}")
        return False

    username, password, host, port, database = match.groups()

    print(f"连接到 MySQL 服务器: {host}:{port}")
    print(f"用户: {username}")
    print(f"数据库: {database}")

    try:
        # 先连接到 MySQL 服务器（不指定数据库）
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            charset='utf8mb4'
        )
        cursor = connection.cursor()

        # 检查数据库是否存在
        cursor.execute(f"SHOW DATABASES LIKE '{database}'")
        result = cursor.fetchone()

        if result:
            print(f"[OK] 数据库 '{database}' 已存在")
        else:
            # 创建数据库
            cursor.execute(f"""
                CREATE DATABASE `{database}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
            """)
            print(f"[OK] 数据库 '{database}' 创建成功")

        cursor.close()
        connection.close()
        return True

    except Exception as e:
        print(f"[ERROR] 创建数据库失败: {e}")
        return False


def create_tables():
    """创建所有表"""
    try:
        print(f"\n连接到数据库 '{settings.database_url}'...")

        # 创建引擎
        engine = create_engine(settings.database_url)

        # 创建所有表
        print("开始创建数据表...")
        Base.metadata.create_all(bind=engine)

        print("[OK] 所有数据表创建成功！")

        # 显示创建的表
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n已创建的表 ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")

        engine.dispose()
        return True

    except Exception as e:
        print(f"[ERROR] 创建数据表失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("RFTIP 数据库初始化")
    print("=" * 50)

    # 1. 创建数据库
    if not create_database():
        print("\n数据库创建失败，终止初始化")
        return

    # 2. 创建表
    if not create_tables():
        print("\n数据表创建失败")
        return

    print("\n" + "=" * 50)
    print("[OK] 数据库初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
