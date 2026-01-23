"""
文件管理相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DataFileBase(BaseModel):
    """数据文件基础模型"""
    is_public: bool = Field(False, description="是否公开")


class DataFileResponse(BaseModel):
    """数据文件响应模型"""
    id: int
    user_id: int
    file_name: str
    file_size: int
    file_type: str
    file_format: Optional[str] = None
    file_hash: Optional[str] = None
    row_count: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    is_public: bool
    upload_time: datetime
    processed_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class DataFileListResponse(BaseModel):
    """数据文件列表响应模型"""
    total: int
    files: list[DataFileResponse]


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    file_id: int
    file_name: str
    status: str
    message: str
