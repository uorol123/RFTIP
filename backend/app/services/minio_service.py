"""
MinIO 对象存储服务
用于处理文件上传、下载等操作
"""
import os
import uuid
from io import BytesIO
from typing import Optional

from minio import Minio
from minio.error import S3Error

from core.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)
from core.logging import logger


class MinIOService:
    """MinIO 对象存储服务"""

    def __init__(self):
        """初始化 MinIO 客户端"""
        self._client: Optional[Minio] = None
        self._bucket = MINIO_BUCKET or "rftip-files"

    @property
    def client(self) -> Minio:
        """获取 MinIO 客户端（懒加载）"""
        if self._client is None:
            if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY]):
                raise ValueError("MinIO 配置不完整，请检查环境变量")

            self._client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE,
            )
            self._ensure_bucket_exists()
        return self._client

    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        try:
            if not self.client.bucket_exists(self._bucket):
                self.client.make_bucket(self._bucket)
                logger.info(f"创建 MinIO 存储桶: {self._bucket}")
        except S3Error as e:
            logger.error(f"MinIO 存储桶操作失败: {e}")
            raise

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        folder: str = "uploads",
        prefix: str = "",
    ) -> str:
        """
        上传文件到 MinIO

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            content_type: MIME 类型
            folder: 存储文件夹
            prefix: 文件名前缀（如用户ID）

        Returns:
            文件访问 URL
        """
        # 生成唯一文件名
        ext = os.path.splitext(filename)[1]
        unique_name = f"{prefix}{uuid.uuid4().hex}{ext}"
        object_name = f"{folder}/{unique_name}"

        try:
            # 上传文件
            self.client.put_object(
                self._bucket,
                object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )

            # 生成访问 URL
            url = self._get_presigned_url(object_name)
            logger.info(f"文件上传成功: {object_name}")
            return url

        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise

    def upload_avatar(
        self,
        file_data: bytes,
        filename: str,
        user_id: int,
    ) -> str:
        """
        上传用户头像

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            user_id: 用户 ID

        Returns:
            object_name（用于存储在数据库）
        """
        # 生成唯一文件名
        ext = os.path.splitext(filename)[1]
        unique_name = f"user_{user_id}_{uuid.uuid4().hex}{ext}"
        object_name = f"avatars/{unique_name}"

        try:
            # 上传文件
            self.client.put_object(
                self._bucket,
                object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type="image/jpeg",
            )
            logger.info(f"头像上传成功: {object_name}")
            return object_name

        except S3Error as e:
            logger.error(f"头像上传失败: {e}")
            raise

    def get_avatar(self, object_name: str) -> tuple[bytes, str]:
        """
        获取头像文件

        Args:
            object_name: 对象名称（如 "avatars/user_1_abc123.jpg"）

        Returns:
            (文件数据, Content-Type)
        """
        try:
            response = self.client.get_object(self._bucket, object_name)
            data = response.read()
            content_type = response.headers.get("Content-Type", "image/jpeg")
            return data, content_type

        except S3Error as e:
            logger.error(f"获取头像失败: {e}")
            raise

    def delete_file(self, object_name: str) -> bool:
        """
        删除文件

        Args:
            object_name: 对象名称（包含路径）

        Returns:
            是否删除成功
        """
        try:
            self.client.remove_object(self._bucket, object_name)
            logger.info(f"文件删除成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"文件删除失败: {e}")
            return False

    def delete_avatar(self, object_name: str) -> bool:
        """
        删除用户头像

        Args:
            object_name: 对象名称（如 "avatars/user_1_abc123.jpg"）

        Returns:
            是否删除成功
        """
        return self.delete_file(object_name)


# 全局单例
minio_service = MinIOService()
