"""
数据文件相关模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.orm import relationship
from core.database import Base


class DataFile(Base):
    """数据文件表"""
    __tablename__ = "data_files"

    id = Column(Integer, primary_key=True, index=True, comment="文件ID")
    user_id = Column(Integer, nullable=False, index=True, comment="上传用户ID")
    file_name = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小（字节）")
    file_type = Column(String(50), nullable=False, comment="文件类型 (csv/excel)")
    file_format = Column(String(50), comment="文件格式 (csv/xlsx/xls)")
    file_hash = Column(String(64), comment="文件哈希值（MD5）")
    row_count = Column(Integer, comment="数据行数")
    status = Column(String(20), default="pending", comment="处理状态 (pending/processing/completed/failed)")
    error_message = Column(Text, comment="错误信息")
    is_public = Column(Integer, default=0, comment="是否公开 (0:私有, 1:公开)")
    upload_time = Column(DateTime, default=datetime.utcnow, comment="上传时间")
    processed_time = Column(DateTime, comment="处理完成时间")

    # 关系
    raw_tracks = relationship("FlightTrackRaw", back_populates="data_file", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DataFile(id={self.id}, file_name='{self.file_name}', status='{self.status}')>"
