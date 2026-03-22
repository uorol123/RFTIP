"""
MinIO 对象存储服务
用于处理文件上传、下载等操作
"""
import asyncio
import os
import time
import uuid
from datetime import timedelta
from io import BytesIO
from typing import Optional

import urllib3
from minio import Minio
from minio.error import S3Error

from core.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)
from core.logging import get_logger


logger = get_logger(__name__)


class MinIOService:
    """MinIO 对象存储服务"""

    def __init__(self):
        """初始化 MinIO 客户端"""
        self._client: Optional[Minio] = None
        self._bucket = MINIO_BUCKET or "rftip-files"
        self._http_pool: Optional[urllib3.PoolManager] = None

    def _get_http_pool(self) -> urllib3.PoolManager:
        """获取 HTTP 连接池（复用 TCP 连接）"""
        if self._http_pool is None:
            self._http_pool = urllib3.PoolManager(
                num_pools=10,           # 连接池数量
                maxsize=10,             # 每个主机的最大连接数
                block=False,            # 连接池满时不阻塞
                timeout=urllib3.Timeout(
                    connect=5.0,        # TCP 连接超时
                    read=30.0,          # 读取超时
                ),
            )
        return self._http_pool

    @property
    def client(self) -> Minio:
        """获取 MinIO 客户端（懒加载，带连接池）"""
        if self._client is None:
            if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY]):
                raise ValueError("MinIO 配置不完整，请检查环境变量")

            self._client = Minio(
                MINIO_ENDPOINT,
                access_key=MINIO_ACCESS_KEY,
                secret_key=MINIO_SECRET_KEY,
                secure=MINIO_SECURE,
                http_client=self._http_pool,
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

    def _get_presigned_url(self, object_name: str, expires: int = 3600 * 24 * 7) -> str:
        """
        生成预签名 URL

        Args:
            object_name: 对象名称
            expires: 过期时间（秒），默认 7 天

        Returns:
            预签名 URL
        """
        try:
            url = self.client.presigned_get_object(
                self._bucket,
                object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            logger.error(f"生成预签名 URL 失败: {e}")
            raise

    def download_file(self, object_name: str) -> bytes:
        """
        下载文件

        Args:
            object_name: 对象名称（包含路径）

        Returns:
            文件二进制数据
        """
        try:
            response = self.client.get_object(self._bucket, object_name)
            data = response.read()
            return data
        except S3Error as e:
            logger.error(f"文件下载失败: {e}")
            raise

    def get_file_url(self, object_name: str, expires: int = 3600 * 24 * 7) -> str:
        """
        获取文件访问 URL（预签名）

        Args:
            object_name: 对象名称
            expires: 过期时间（秒），默认 7 天

        Returns:
            预签名 URL
        """
        return self._get_presigned_url(object_name, expires)

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        folder: str = "uploads",
        prefix: str = "",
    ) -> str:
        """
        上传文件到 MinIO（返回 URL）

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

    def upload_data_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        folder: str = "trajectory",
        prefix: str = "",
    ) -> tuple[str, str]:
        """
        上传数据文件到 MinIO（返回对象名称和 URL）

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            content_type: MIME 类型
            folder: 存储文件夹（trajectory 或 radar_station）
            prefix: 文件名前缀（如用户ID）

        Returns:
            (object_name, url) 对象名称和访问 URL
        """
        # 生成唯一文件名
        ext = os.path.splitext(filename)[1]
        unique_name = f"{prefix}{uuid.uuid4().hex}{ext}"
        object_name = f"{folder}/{unique_name}"

        import time
        start_time = time.time()

        try:
            # 上传文件 - 小文件(<5MB)不使用分片上传
            part_size = 0 if len(file_data) < 5 * 1024 * 1024 else None

            upload_start = time.time()
            self.client.put_object(
                self._bucket,
                object_name,
                data=BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
                part_size=part_size,
            )
            upload_elapsed = time.time() - upload_start
            logger.info(f"MinIO put_object 耗时: {upload_elapsed:.3f}s")

            # 生成访问 URL（本地开发可以直接用 object_name 构造 URL，避免额外请求）
            url_start = time.time()
            url = self._get_presigned_url(object_name)
            url_elapsed = time.time() - url_start
            logger.info(f"MinIO presigned URL 耗时: {url_elapsed:.3f}s")

            total_elapsed = time.time() - start_time
            logger.info(f"数据文件上传成功: {object_name}, 总耗时: {total_elapsed:.3f}s")
            return object_name, url

        except S3Error as e:
            logger.error(f"数据文件上传失败: {e}")
            raise

    async def upload_data_file_async(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        folder: str = "trajectory",
        prefix: str = "",
    ) -> tuple[str, str]:
        """
        异步上传数据文件到 MinIO（在线程池中执行）

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            content_type: MIME 类型
            folder: 存储文件夹（trajectory 或 radar_station）
            prefix: 文件名前缀（如用户ID）

        Returns:
            (object_name, url) 对象名称和访问 URL
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.upload_data_file,
            file_data,
            filename,
            content_type,
            folder,
            prefix,
        )

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
