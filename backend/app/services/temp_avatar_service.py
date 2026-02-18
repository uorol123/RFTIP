"""
临时头像服务
使用 Redis 存储用户上传的临时头像，用于注册前的预览
"""
import uuid
import pickle
from typing import Optional

from core.config import REDIS_URL
from core.logging import get_logger


logger = get_logger(__name__)


class TempAvatarService:
    """临时头像服务"""

    # Redis key 前缀
    KEY_PREFIX = "temp_avatar:"
    # 默认过期时间（秒）
    DEFAULT_TTL = 3600  # 1 小时

    def __init__(self):
        """初始化 Redis 客户端（懒加载）"""
        self._redis = None

    @property
    def redis(self):
        """获取 Redis 客户端"""
        if self._redis is None:
            try:
                import redis
                self._redis = redis.from_url(REDIS_URL)
                logger.info("Redis 连接成功")
            except ImportError:
                raise ImportError("请安装 redis 库: pip install redis")
            except Exception as e:
                logger.error(f"Redis 连接失败: {e}")
                raise
        return self._redis

    def save_temp_avatar(self, file_data: bytes, content_type: str = "image/jpeg") -> str:
        """
        保存临时头像到 Redis

        Args:
            file_data: 文件二进制数据
            content_type: MIME 类型

        Returns:
            temp_token（用于后续获取和注册）
        """
        # 生成唯一的 temp_token
        temp_token = uuid.uuid4().hex

        # 构造 Redis key
        key = f"{self.KEY_PREFIX}{temp_token}"

        # 序列化数据
        data = {
            "file_data": file_data,
            "content_type": content_type,
        }

        try:
            # 存储到 Redis，设置过期时间
            self.redis.setex(
                key,
                self.DEFAULT_TTL,
                pickle.dumps(data)
            )
            logger.info(f"临时头像已保存: {temp_token}, TTL: {self.DEFAULT_TTL}s")
            return temp_token

        except Exception as e:
            logger.error(f"保存临时头像失败: {e}")
            raise

    def get_temp_avatar(self, temp_token: str) -> Optional[tuple[bytes, str]]:
        """
        获取临时头像

        Args:
            temp_token: 临时令牌

        Returns:
            (文件数据, Content-Type) 或 None
        """
        key = f"{self.KEY_PREFIX}{temp_token}"

        try:
            data = self.redis.get(key)
            if data is None:
                return None

            # 反序列化
            avatar_data = pickle.loads(data)
            return avatar_data["file_data"], avatar_data["content_type"]

        except Exception as e:
            logger.error(f"获取临时头像失败: {e}")
            return None

    def delete_temp_avatar(self, temp_token: str) -> bool:
        """
        删除临时头像

        Args:
            temp_token: 临时令牌

        Returns:
            是否删除成功
        """
        key = f"{self.KEY_PREFIX}{temp_token}"

        try:
            self.redis.delete(key)
            logger.info(f"临时头像已删除: {temp_token}")
            return True

        except Exception as e:
            logger.error(f"删除临时头像失败: {e}")
            return False


# 全局单例
temp_avatar_service = TempAvatarService()
