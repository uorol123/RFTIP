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

# 中文列名到英文列名的映射
COLUMN_NAME_MAPPING = {
    # 中文 -> 英文
    "批号": "track_id",           # 飞机ID
    "日期": "date",               # 日期 YYYYMMDD
    "入库时间": "timestamp",      # 完整时间戳（优先使用）
    "纬度": "latitude",
    "经度": "longitude",
    "高度": "altitude",
    "速度": "speed",
    "航向": "heading",
    "站号": "radar_station_id",   # 雷达站ID
    # 英文 -> 英文（兼容原有格式）
    "track_id": "track_id",
    "timestamp": "timestamp",
    "date": "date",
    "latitude": "latitude",
    "longitude": "longitude",
    "altitude": "altitude",
    "speed": "speed",
    "heading": "heading",
    "radar_station_id": "radar_station_id",
}


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


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    标准化列名：将中文列名映射为英文列名

    支持的中文列名：
    - 批号 -> track_id（飞机ID）
    - 站号 -> radar_station_id（雷达站ID）
    - 入库时间 -> timestamp（完整时间戳，优先使用）
    - 日期 -> date（YYYYMMDD格式，仅日期）
    - 纬度 -> latitude
    - 经度 -> longitude
    - 高度 -> altitude
    - 速度 -> speed
    - 航向 -> heading
    """
    # 创建列名映射字典（只映射存在的列）
    rename_mapping = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_NAME_MAPPING:
            rename_mapping[col] = COLUMN_NAME_MAPPING[col_stripped]

    # 重命名列
    if rename_mapping:
        df = df.rename(columns=rename_mapping)

    return df


def validate_track_data(df: pd.DataFrame) -> List[str]:
    """
    验证轨迹数据格式

    支持中英文列名：
    - 必需列（中文）: 批号, 入库时间/日期, 纬度, 经度
    - 必需列（英文）: track_id, timestamp, latitude, longitude

    字段说明：
    - 批号: 飞机ID (track_id)
    - 站号: 雷达站ID (radar_station_id)
    - 入库时间: 完整时间戳 (timestamp，优先使用)
    - 日期: 日期 YYYYMMDD (仅日期，作为备用)
    """
    # 先标准化列名
    df_normalized = normalize_column_names(df.copy())

    # 检查必需列（使用标准化后的列名）
    # timestamp 可以是 "入库时间" 或 "日期"
    required_columns = ["track_id", "latitude", "longitude"]
    timestamp_sources = ["timestamp", "date", "日期"]  # 至少需要一个时间列
    missing_columns = []

    for req_col in required_columns:
        # 检查英文列名
        if req_col in df_normalized.columns:
            continue
        # 检查对应的中文列名
        chinese_col = next((k for k, v in COLUMN_NAME_MAPPING.items() if v == req_col), None)
        if chinese_col and chinese_col in df.columns:
            continue
        missing_columns.append(f"{req_col} ({chinese_col or 'N/A'})")

    # 检查是否至少有一个时间列
    has_timestamp = any(col in df_normalized.columns or col in df.columns for col in timestamp_sources)
    if not has_timestamp:
        missing_columns.append("timestamp (入库时间/日期)")

    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"缺少必需的列: {', '.join(missing_columns)}。\n"
                   f"支持中英文列名：\n"
                   f"  - 批号/track_id（飞机ID）\n"
                   f"  - 入库时间/timestamp（完整时间戳）\n"
                   f"  - 日期/date（YYYYMMDD，可替代入库时间）\n"
                   f"  - 纬度/latitude（纬度）\n"
                   f"  - 经度/longitude（经度）",
        )

    # 验证数据类型和范围
    errors = []

    # 获取纬度列（可能是中文或英文）
    lat_col = "latitude" if "latitude" in df_normalized.columns else "纬度"
    if lat_col in df_normalized.columns:
        if not df_normalized[lat_col].between(-90, 90).all():
            errors.append("纬度值必须在 -90 到 90 之间")

    # 获取经度列
    lng_col = "longitude" if "longitude" in df_normalized.columns else "经度"
    if lng_col in df_normalized.columns:
        if not df_normalized[lng_col].between(-180, 180).all():
            errors.append("经度值必须在 -180 到 180 之间")

    return errors


def parse_timestamp(value, fallback_date=None) -> datetime:
    """
    解析时间戳，支持多种格式

    支持格式：
    - 完整时间戳: 2025-11-25 22:00:00.500000
    - 标准 datetime 格式: 2025-11-25 22:00:00
    - 整数日期格式: 20251125 (fallback_date)

    Args:
        value: 主要时间值（入库时间）
        fallback_date: 备用日期值（日期字段，YYYYMMDD格式）
    """
    # 优先使用完整时间戳
    if pd.notna(value):
        value_str = str(value).strip()
        try:
            # 尝试标准解析
            return pd.to_datetime(value_str)
        except:
            pass

    # 如果没有完整时间戳，尝试使用备用日期
    if pd.notna(fallback_date):
        fallback_str = str(fallback_date).strip()
        if fallback_str.isdigit() and len(fallback_str) == 8:
            year = fallback_str[:4]
            month = fallback_str[4:6]
            day = fallback_str[6:8]
            return pd.to_datetime(f"{year}-{month}-{day}")

    raise ValueError("无法解析时间：需要有效的入库时间或日期")


def process_file_data(file_id: int, db: Session) -> dict:
    """
    处理文件数据并导入到数据库

    支持中英文列名：

    中文列名:
    - 批号: 飞机ID (track_id)
    - 站号: 雷达站ID (radar_station_id)
    - 入库时间: 完整时间戳，优先使用 (timestamp)
    - 日期: 日期 YYYYMMDD，作为备用 (date)
    - 纬度: 纬度 (latitude)
    - 经度: 经度 (longitude)
    - 高度: 高度米 (altitude)
    - 速度: 速度 (speed)
    - 航向: 航向度 (heading)

    英文列名:
    - track_id: 飞机ID
    - radar_station_id: 雷达站ID
    - timestamp: 完整时间戳
    - date: 日期 (备用)
    - latitude: 纬度
    - longitude: 经度
    - altitude: 高度
    - speed: 速度
    - heading: 航向

    时间戳解析规则:
    1. 优先使用 "入库时间/timestamp" (完整时间戳)
    2. 如果没有，使用 "日期/date" (YYYYMMDD 格式)
    """
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

        # 标准化列名（中文 -> 英文）
        df = normalize_column_names(df)

        # 验证数据
        validate_track_data(df)

        # 导入数据
        row_count = 0
        for _, row in df.iterrows():
            # 解析时间戳（优先使用入库时间，fallback 到日期）
            timestamp = parse_timestamp(
                value=row.get("timestamp"),       # 入库时间（完整时间戳）
                fallback_date=row.get("date")     # 日期（YYYYMMDD）
            )

            track_point = FlightTrackRaw(
                file_id=file_id,
                track_id=str(row.get("track_id")),
                timestamp=timestamp,
                latitude=float(row.get("latitude")),
                longitude=float(row.get("longitude")),
                altitude=float(row.get("altitude") or 0) if pd.notna(row.get("altitude")) else None,
                speed=float(row.get("speed") or 0) if pd.notna(row.get("speed")) else None,
                heading=float(row.get("heading") or 0) if pd.notna(row.get("heading")) else None,
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
