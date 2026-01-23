"""
文件管理服务 - 处理文件上传、解析、存储和删除
"""
import os
import hashlib
import json
import pandas as pd
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from core.config import get_settings
from app.models.data_file import DataFile
from app.models.flight_track import FlightTrackRaw
from app.schemas.file import DataFileResponse, FileUploadResponse

settings = get_settings()

# 支持的文件类型
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
FILE_TYPE_MAP = {".csv": "csv", ".xlsx": "excel", ".xls": "excel"}


def get_file_hash(file_content: bytes) -> str:
    """计算文件哈希值（MD5）"""
    return hashlib.md5(file_content).hexdigest()


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


async def save_uploaded_file(file: UploadFile, user_id: int, db: Session) -> FileUploadResponse:
    """保存上传的文件"""
    # 验证文件类型
    file_ext = get_file_extension(file.filename)
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 读取文件内容
    file_content = await file.read()
    file_size = len(file_content)
    file_hash = get_file_hash(file_content)

    # 创建存储目录
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # 生成唯一文件名
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{user_id}_{timestamp}_{file_hash[:8]}{file_ext}"
    file_path = os.path.join(upload_dir, safe_filename)

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(file_content)

    # 创建数据库记录
    db_file = DataFile(
        user_id=user_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=FILE_TYPE_MAP[file_ext],
        file_format=file_ext[1:],
        file_hash=file_hash,
        status="pending",
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return FileUploadResponse(
        file_id=db_file.id,
        file_name=db_file.file_name,
        status=db_file.status,
        message="文件上传成功，等待处理",
    )


def parse_csv_file(file_path: str) -> pd.DataFrame:
    """解析 CSV 文件"""
    try:
        # 尝试不同的编码
        for encoding in ["utf-8", "gbk", "gb2312", "latin1"]:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                return df
            except UnicodeDecodeError:
                continue
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法解析文件编码",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV 解析错误: {str(e)}",
        )


def parse_excel_file(file_path: str) -> pd.DataFrame:
    """解析 Excel 文件"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Excel 解析错误: {str(e)}",
        )


def validate_track_data(df: pd.DataFrame) -> List[str]:
    """验证轨迹数据格式"""
    required_columns = ["track_id", "timestamp", "latitude", "longitude"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"缺少必需的列: {', '.join(missing_columns)}。必需列: {', '.join(required_columns)}",
        )

    # 验证数据类型和范围
    errors = []
    if not df["latitude"].between(-90, 90).all():
        errors.append("纬度值必须在 -90 到 90 之间")
    if not df["longitude"].between(-180, 180).all():
        errors.append("经度值必须在 -180 到 180 之间")

    return errors


def process_file_data(file_id: int, db: Session) -> dict:
    """处理文件数据并导入到数据库"""
    db_file = db.query(DataFile).filter(DataFile.id == file_id).first()
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在",
        )

    try:
        # 更新状态为处理中
        db_file.status = "processing"
        db.commit()

        # 解析文件
        if db_file.file_type == "csv":
            df = parse_csv_file(db_file.file_path)
        else:
            df = parse_excel_file(db_file.file_path)

        # 验证数据
        validate_track_data(df)

        # 导入数据
        row_count = 0
        for _, row in df.iterrows():
            track_point = FlightTrackRaw(
                file_id=file_id,
                track_id=str(row["track_id"]),
                timestamp=pd.to_datetime(row["timestamp"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                altitude=float(row.get("altitude", 0)) if pd.notna(row.get("altitude")) else None,
                speed=float(row.get("speed", 0)) if pd.notna(row.get("speed")) else None,
                heading=float(row.get("heading", 0)) if pd.notna(row.get("heading")) else None,
                raw_data=json.dumps(row.to_dict()),
            )
            db.add(track_point)
            row_count += 1

        # 更新文件状态
        db_file.row_count = row_count
        db_file.status = "completed"
        db_file.processed_time = datetime.utcnow()
        db.commit()

        return {
            "total_points": row_count,
            "status": "completed",
        }

    except Exception as e:
        # 更新状态为失败
        db_file.status = "failed"
        db_file.error_message = str(e)
        db.commit()
        raise


def get_file_by_id(file_id: int, db: Session, user_id: Optional[int] = None) -> Optional[DataFile]:
    """根据 ID 获取文件"""
    query = db.query(DataFile).filter(DataFile.id == file_id)
    if user_id is not None:
        query = query.filter(
            (DataFile.user_id == user_id) | (DataFile.is_public == 1)
        )
    return query.first()


def get_user_files(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[DataFile], int]:
    """获取用户的文件列表"""
    query = db.query(DataFile).filter(DataFile.user_id == user_id)
    total = query.count()
    files = query.order_by(DataFile.upload_time.desc()).offset(skip).limit(limit).all()
    return files, total


def delete_file(file_id: int, db: Session, user_id: int) -> bool:
    """删除文件"""
    db_file = db.query(DataFile).filter(
        DataFile.id == file_id,
        DataFile.user_id == user_id
    ).first()

    if not db_file:
        return False

    # 删除物理文件
    if os.path.exists(db_file.file_path):
        os.remove(db_file.file_path)

    # 删除数据库记录（级联删除关联的轨迹数据）
    db.delete(db_file)
    db.commit()
    return True
