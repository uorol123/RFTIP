"""
文件管理相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, computed_field


class DataFileBase(BaseModel):
    """数据文件基础模型"""
    is_public: bool = Field(False, description="是否公开")


class DataFileUpdateVisibility(BaseModel):
    """文件可见性更新模型"""
    is_public: bool = Field(..., description="是否公开")


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

    # 前端兼容字段
    @computed_field
    @property
    def filename(self) -> str:
        return self.file_name

    @computed_field
    @property
    def original_filename(self) -> str:
        return self.file_name

    @computed_field
    @property
    def owner_id(self) -> int:
        return self.user_id

    @computed_field
    @property
    def record_count(self) -> Optional[int]:
        return self.row_count

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


class FileStatusResponse(BaseModel):
    """文件处理状态响应模型"""
    file_id: int
    status: str
    progress: float = Field(0.0, ge=0, le=100, description="处理进度（百分比）")
    message: Optional[str] = None
    processed_rows: Optional[int] = None
    total_rows: Optional[int] = None
