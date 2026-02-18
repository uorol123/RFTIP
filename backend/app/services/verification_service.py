"""
验证码服务模块
负责生成、存储和验证验证码
"""
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VerificationCodeService:
    """
    验证码服务（内存存储）
    适用于单实例应用，生产环境建议使用 Redis
    """

    def __init__(self):
        # 存储结构: {email: {"code": "123456", "expire_at": datetime}}
        self._codes: dict[str, dict] = {}

    def generate_code(self, length: int = None) -> str:
        """
        生成随机数字验证码

        Args:
            length: 验证码长度，默认使用配置中的长度

        Returns:
            str: 生成的验证码
        """
        length = length or settings.verification_code_length
        # 生成纯数字验证码
        code = ''.join(random.choices(string.digits, k=length))
        return code

    def store_code(self, email: str, code: str, expire_minutes: int = None) -> None:
        """
        存储验证码

        Args:
            email: 邮箱地址
            code: 验证码
            expire_minutes: 过期时间（分钟），默认使用配置中的时间
        """
        expire_minutes = expire_minutes or settings.verification_code_expire_minutes
        expire_at = datetime.now() + timedelta(minutes=expire_minutes)

        self._codes[email] = {
            "code": code,
            "expire_at": expire_at
        }

        # 在日志中打印验证码（方便调试）
        if settings.log_verification_code:
            # 使用 print 确保验证码一定能在控制台看到
            print("=" * 50)
            print("📧 邮箱验证码")
            print(f"邮箱: {email}")
            print(f"验证码: {code}")
            print(f"有效期: {expire_minutes} 分钟")
            print(f"过期时间: {expire_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)

    def verify_code(self, email: str, code: str, consume: bool = True) -> bool:
        """
        验证验证码

        Args:
            email: 邮箱地址
            code: 用户输入的验证码
            consume: 验证成功后是否删除验证码（默认True）

        Returns:
            bool: 验证是否成功
        """
        # 检查邮箱是否有验证码记录
        if email not in self._codes:
            logger.warning(f"验证码验证失败: 邮箱 {email} 无验证码记录")
            return False

        stored_data = self._codes[email]
        stored_code = stored_data["code"]
        expire_at = stored_data["expire_at"]

        # 检查验证码是否正确
        if stored_code != code:
            logger.warning(f"验证码验证失败: 邮箱 {email} 验证码错误")
            return False

        # 检查是否过期
        if datetime.now() > expire_at:
            logger.warning(f"验证码验证失败: 邮箱 {email} 验证码已过期")
            # 删除过期的验证码
            del self._codes[email]
            return False

        # 验证成功，记录日志
        logger.info(f"验证码验证成功: 邮箱 {email}")

        # 验证成功后删除验证码（一次性使用）
        if consume:
            del self._codes[email]

        return True

    def has_pending_code(self, email: str) -> bool:
        """
        检查邮箱是否有待处理的验证码（未过期）

        Args:
            email: 邮箱地址

        Returns:
            bool: 是否有待处理的验证码
        """
        if email not in self._codes:
            return False

        # 检查是否过期
        expire_at = self._codes[email]["expire_at"]
        if datetime.now() > expire_at:
            # 清理过期验证码
            del self._codes[email]
            return False

        return True

    def get_remaining_time(self, email: str) -> Optional[int]:
        """
        获取验证码剩余有效时间（秒）

        Args:
            email: 邮箱地址

        Returns:
            int | None: 剩余秒数，如果验证码不存在或已过期返回 None
        """
        if email not in self._codes:
            return None

        expire_at = self._codes[email]["expire_at"]
        if datetime.now() > expire_at:
            del self._codes[email]
            return None

        remaining = int((expire_at - datetime.now()).total_seconds())
        return max(0, remaining)

    def cleanup_expired(self) -> int:
        """
        清理过期的验证码

        Returns:
            int: 清理的数量
        """
        expired_keys = []
        now = datetime.now()

        for email, data in self._codes.items():
            if now > data["expire_at"]:
                expired_keys.append(email)

        for key in expired_keys:
            del self._codes[key]

        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期验证码")

        return len(expired_keys)


# 全局验证码服务实例
verification_service = VerificationCodeService()
