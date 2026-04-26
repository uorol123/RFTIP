"""
文件管理服务 - 处理文件上传、解析、存储和删除
"""
import hashlib
import json
import os
import pandas as pd
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile
from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.models.data_file import DataFile
from app.models.flight_track import FlightTrackRaw, RadarStation
from app.schemas.file import DataFileResponse, FileUploadResponse
from app.services.minio_service import minio_service
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# 支持的文件类型
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
FILE_TYPE_MAP = {".csv": "csv", ".xlsx": "excel", ".xls": "excel"}

# 中文列名到英文列名的映射
COLUMN_NAME_MAPPING = {
    # 轨迹数据列名
    "批号": "batch_id",           # 飞机批号
    "日期": "date",               # 日期 YYYYMMDD
    "入库时间": "timestamp",      # 完整时间戳（优先使用）
    "纬度": "latitude",
    "经度": "longitude",
    "高度": "altitude",
    "速度": "speed",
    "站号": "station_id",         # 雷达站号
    # 英文 -> 英文（兼容原有格式）
    "batch_id": "batch_id",
    "station_id": "station_id",
    "track_id": "batch_id",       # 兼容旧格式
    "timestamp": "timestamp",
    "date": "date",
    "latitude": "latitude",
    "longitude": "longitude",
    "altitude": "altitude",
    "speed": "speed",
}


def get_file_hash(file_content: bytes) -> str:
    """计算文件哈希值（MD5）"""
    return hashlib.md5(file_content).hexdigest()


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


async def save_uploaded_file(
    file: UploadFile,
    user_id: int,
    db: Session,
    category: str = "trajectory"
) -> FileUploadResponse:
    """保存上传的文件到 MinIO"""
    import time
    total_start = time.time()

    # 验证文件类型
    file_ext = get_file_extension(file.filename)
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}")

    # 读取文件内容
    read_start = time.time()
    file_content = await file.read()
    read_elapsed = time.time() - read_start
    logger.info(f"文件读取耗时: {read_elapsed:.3f}s, 大小: {len(file_content)} bytes")

    file_size = len(file_content)
    file_hash = get_file_hash(file_content)

    # 确定 MIME 类型
    content_type_map = {
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
    }
    content_type = content_type_map.get(file_ext, "application/octet-stream")

    # 上传到 MinIO（异步执行，不阻塞事件循环）
    minio_object_name, minio_url = await minio_service.upload_data_file_async(
        file_data=file_content,
        filename=file.filename,
        content_type=content_type,
        folder="trajectory" if category == "trajectory" else "radar_station",
        prefix=f"{user_id}_",
    )

    # 创建数据库记录
    db_start = time.time()
    db_file = DataFile(
        user_id=user_id,
        file_name=file.filename,
        file_path=minio_object_name,  # 存储 MinIO 对象名称
        file_size=file_size,
        file_type=FILE_TYPE_MAP[file_ext],
        file_format=file_ext[1:],
        file_hash=file_hash,
        category=category,  # 保存文件分类
        status="pending",
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    db_elapsed = time.time() - db_start
    logger.info(f"数据库操作耗时: {db_elapsed:.3f}s")

    total_elapsed = time.time() - total_start
    logger.info(f"上传接口总耗时: {total_elapsed:.3f}s")

    return FileUploadResponse(
        file_id=db_file.id,
        file_name=db_file.file_name,
        status=db_file.status,
        file_size=db_file.file_size,
        category=category,
        message="文件上传成功，正在处理",
    )


def parse_csv_file(file_content: bytes) -> pd.DataFrame:
    """解析 CSV 文件内容"""
    import io

    # 尝试不同的编码
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "gb18030", "latin1", "cp1252", "iso-8859-1"]
    last_error = None

    for encoding in encodings:
        try:
            df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
            # 验证数据是否有效（至少有一列）
            if len(df.columns) > 0:
                logger.info(f"CSV 文件解析成功，使用编码: {encoding}")
                return df
        except (UnicodeDecodeError, UnicodeError) as e:
            last_error = e
            continue
        except Exception as e:
            # 如果是编码以外的问题，直接抛出
            if "encoding" not in str(e).lower():
                raise ValueError(f"CSV 解析错误: {str(e)}")
            last_error = e
            continue

    # 所有编码都失败
    raise ValueError(f"无法解析文件编码，尝试过的编码: {', '.join(encodings)}。最后错误: {last_error}")


def parse_excel_file(file_content: bytes) -> pd.DataFrame:
    """解析 Excel 文件内容"""
    try:
        df = pd.read_excel(file_content)
        # 验证数据是否有效
        if len(df.columns) == 0:
            raise ValueError("Excel 文件没有可读取的列")
        logger.info(f"Excel 文件解析成功，共 {len(df)} 行, {len(df.columns)} 列")
        return df
    except Exception as e:
        raise ValueError(f"Excel 解析错误: {str(e)}")


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
    - 必需列（英文）: batch_id, timestamp, latitude, longitude

    字段说明：
    - 批号: 飞机批号 (batch_id)
    - 站号: 雷达站号 (station_id)
    - 入库时间: 完整时间戳 (timestamp，优先使用)
    - 日期: 日期 YYYYMMDD (仅日期，作为备用)
    """
    # 先标准化列名
    df_normalized = normalize_column_names(df.copy())

    # 检查必需列（使用标准化后的列名）
    # timestamp 可以是 "入库时间" 或 "日期"
    required_columns = ["batch_id", "latitude", "longitude"]
    timestamp_sources = ["timestamp", "date", "日期"]  # 至少需要一个时间列
    missing_columns = []

    for req_col in required_columns:
        # 检查英文列名
        if req_col in df_normalized.columns:
            continue
        # 特殊处理 latitude/longitude 的中文列名
        if req_col == "latitude" and "纬度" in df.columns:
            continue
        if req_col == "longitude" and "经度" in df.columns:
            continue
        missing_columns.append(f"{req_col}")

    # 检查是否至少有一个时间列
    has_timestamp = any(col in df_normalized.columns or col in df.columns for col in timestamp_sources)
    if not has_timestamp:
        missing_columns.append("timestamp (入库时间/日期)")

    if missing_columns:
        raise ValueError(
            f"缺少必需的列: {', '.join(missing_columns)}。\n"
            f"支持中英文列名：\n"
            f"  - 批号/batch_id（飞机批号）\n"
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


def validate_radar_station_data(df: pd.DataFrame) -> List[str]:
    """
    验证雷达站配置数据格式

    支持中英文列名：
    - 必需列: 站号/station_id, 经度/longitude, 纬度/latitude
    - 可选列: 高度/altitude, 描述/description
    """
    # 雷达站列名映射（先处理，避免被通用映射覆盖）
    station_column_mapping = {
        "站号": "station_id",
        "雷达站编号": "station_id",
        "经度": "longitude",
        "纬度": "latitude",
        "高度": "altitude",
        "描述": "description",
        "备注": "description",
    }

    # 先重命名雷达站专用列
    df_temp = df.copy()
    for cn_col, en_col in station_column_mapping.items():
        if cn_col in df_temp.columns:
            df_temp = df_temp.rename(columns={cn_col: en_col})

    # 再标准化其他列名
    df_normalized = normalize_column_names(df_temp)

    # 检查必需列
    required_columns = ["station_id", "latitude", "longitude"]
    missing_columns = []

    for req_col in required_columns:
        # 检查英文列名
        if req_col in df_normalized.columns:
            continue
        # 特殊处理：纬度/经度/站号
        if req_col == "station_id" and "站号" in df.columns:
            continue
        if req_col == "latitude" and "纬度" in df.columns:
            continue
        if req_col == "longitude" and "经度" in df.columns:
            continue
        missing_columns.append(f"{req_col}")

    if missing_columns:
        raise ValueError(
            f"缺少必需的列: {', '.join(missing_columns)}。\n"
            f"支持中英文列名：\n"
            f"  - 站号/station_id（雷达站编号，必需）\n"
            f"  - 经度/longitude（必需）\n"
            f"  - 纬度/latitude（必需）\n"
            f"  - 高度/altitude（可选，单位：米）\n"
            f"  - 描述/description（可选）"
        )

    # 验证数据类型和范围
    errors = []

    # 获取纬度列
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
        except Exception:
            pass

    # 如果没有完整时间戳，尝试使用备用日期
    if pd.notna(fallback_date):
        fallback_str = str(fallback_date).strip()
        if fallback_str.isdigit() and len(fallback_str) == 8:
            year = fallback_str[:4]
            month = fallback_str[4:6]
            day = fallback_str[6:8]
            try:
                return pd.to_datetime(f"{year}-{month}-{day}")
            except Exception as e:
                raise ValueError(f"无法解析日期 {fallback_str}: {e}")

    raise ValueError(f"无法解析时间：value={value}, fallback_date={fallback_date}")


def process_file_data(file_id: int, db: Session, websocket_manager=None, loop=None) -> dict:
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
    import asyncio

    def send_ws_notification(data):
        """发送WebSocket通知（线程安全）"""
        if websocket_manager and loop:
            asyncio.run_coroutine_threadsafe(
                websocket_manager.broadcast_to_file(file_id, data),
                loop
            )

    db_file = db.query(DataFile).filter(DataFile.id == file_id).first()
    if not db_file:
        raise ValueError(f"文件不存在: file_id={file_id}")

    # 更新状态为处理中
    db_file.status = "processing"
    db.commit()

    try:
        # 通知：开始处理
        send_ws_notification({
            "type": "progress",
            "file_id": file_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "status": "processing",
                "progress": 10.0,
                "stage": "解析中",
                "processed_rows": 0,
                "total_rows": 0,
                "message": "正在解析文件..."
            }
        })

        # 从 MinIO 下载文件内容
        file_content = minio_service.download_file(db_file.file_path)

        # 解析文件
        if db_file.file_type == "csv":
            df = parse_csv_file(file_content)
        else:
            df = parse_excel_file(file_content)

        total_rows = len(df)

        # 通知：解析完成，开始预处理
        send_ws_notification({
                "type": "progress",
                "file_id": file_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "status": "processing",
                    "progress": 30.0,
                    "stage": "预处理中",
                    "processed_rows": 0,
                    "total_rows": total_rows,
                    "message": "正在预处理数据..."
                }
        })

        # 根据文件类型进行不同的处理
        if db_file.category == "radar_station":
            # 雷达站配置数据处理（不使用通用列名标准化，避免站号被映射为radar_station_id）
            return _process_radar_station_data(file_id, db, df, total_rows, send_ws_notification)
        else:
            # 轨迹数据处理 - 需要标准化列名
            df = normalize_column_names(df)
            return _process_track_data(file_id, db, df, total_rows, send_ws_notification)

    except Exception as e:
        # 记录错误
        logger.error(f"处理文件 {file_id} 时发生错误: {e}", exc_info=True)

        # 更新状态为失败
        db_file = db.query(DataFile).filter(DataFile.id == file_id).first()
        if db_file:
            db_file.status = "failed"
            # 限制错误消息长度
            error_msg = str(e)
            if len(error_msg) > 500:
                error_msg = error_msg[:500] + "..."
            db_file.error_message = error_msg
            db.commit()

            # 通知：处理失败
            send_ws_notification({
                "type": "error",
                "file_id": file_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "message": error_msg
                }
            })

        # 返回错误信息而不是抛出异常（因为在异步任务中）
        return {
            "status": "failed",
            "error": str(e)
        }


def _process_track_data(file_id: int, db: Session, df: pd.DataFrame, total_rows: int, send_ws_notification) -> dict:
    """处理轨迹数据"""
    import json
    from sqlalchemy import insert
    from app.models.flight_track import FlightTrackRaw, RadarStation

    # 验证数据
    validate_track_data(df)

    # 预加载所有雷达站，建立 station_id -> id 的映射
    radar_stations = db.query(RadarStation.station_id, RadarStation.id).all()
    station_id_to_db_id = {code: id for code, id in radar_stations}
    logger.info(f"已加载 {len(station_id_to_db_id)} 个雷达站映射")

    batch_size = 2000  # 每批插入数量
    row_count = 0
    batch_data = []

    # 将 DataFrame 转换为字典列表（比 iterrows 快得多）
    records = df.to_dict('records')

    for idx, row in enumerate(records):
        # 解析时间戳（优先使用入库时间，fallback 到日期）
        timestamp = parse_timestamp(
            value=row.get("timestamp"),
            fallback_date=row.get("date")
        )

        # 获取站号并转换为雷达站ID
        station_id = str(row.get("station_id", "")).strip()
        radar_station_db_id = station_id_to_db_id.get(station_id)

        # 构建插入数据字典
        track_data = {
            "file_id": file_id,
            "batch_id": str(row.get("batch_id")),
            "station_id": station_id,
            "radar_station_id": radar_station_db_id,  # 可能为None如果雷达站不存在
            "timestamp": timestamp,
            "latitude": float(row.get("latitude")),
            "longitude": float(row.get("longitude")),
            "altitude": float(row.get("altitude") or 0) if pd.notna(row.get("altitude")) else None,
            "speed": float(row.get("speed") or 0) if pd.notna(row.get("speed")) else None,
        }
        batch_data.append(track_data)
        row_count += 1

        # 批量插入
        if len(batch_data) >= batch_size:
            db.execute(insert(FlightTrackRaw).values(batch_data))
            db.commit()  # 每批提交一次
            batch_data = []

            # 每批发送一次进度更新
            progress = 30.0 + (row_count / total_rows * 50)
            send_ws_notification({
                "type": "progress",
                "file_id": file_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "status": "processing",
                    "progress": progress,
                    "stage": "存储中",
                    "processed_rows": row_count,
                    "total_rows": total_rows,
                    "message": f"正在存储数据... ({row_count}/{total_rows})"
                }
            })

    # 插入剩余数据
    if batch_data:
        db.execute(insert(FlightTrackRaw).values(batch_data))

    # 更新文件状态
    db_file = db.query(DataFile).filter(DataFile.id == file_id).first()
    db_file.row_count = row_count
    db_file.status = "completed"
    db_file.processed_time = datetime.utcnow()
    db.commit()

    # 通知：处理完成
    send_ws_notification({
        "type": "completed",
        "file_id": file_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "status": "completed",
            "progress": 100.0,
            "stage": "完成",
            "processed_rows": row_count,
            "total_rows": row_count,
            "message": f"处理完成，共 {row_count} 条记录"
        }
    })

    return {
        "row_count": row_count,
        "message": "轨迹数据处理完成"
    }


def _process_radar_station_data(file_id: int, db: Session, df: pd.DataFrame, total_rows: int, send_ws_notification) -> dict:
    """处理雷达站配置数据"""
    import json
    from sqlalchemy import insert
    from app.models.flight_track import RadarStation

    # 验证数据
    validate_radar_station_data(df)

    # 雷达站列名特殊处理
    station_column_mapping = {
        "站号": "station_id",
        "雷达站编号": "station_id",
        "经度": "longitude",
        "纬度": "latitude",
        "高度": "altitude",
        "描述": "description",
        "备注": "description",
    }

    # 应用雷达站专用列名映射
    for cn_col, en_col in station_column_mapping.items():
        if cn_col in df.columns:
            df = df.rename(columns={cn_col: en_col})

    row_count = 0
    updated_count = 0
    inserted_count = 0

    records = df.to_dict('records')

    for idx, row in enumerate(records):
        station_id = str(row.get("station_id", "")).strip()

        if not station_id:
            continue

        # 检查是否已存在（按station_id查重，但允许同一station_id来自不同文件）
        existing = db.query(RadarStation).filter(
            RadarStation.station_id == station_id
        ).first()

        station_data = {
            "file_id": file_id,
            "station_id": station_id,
            "latitude": float(row.get("latitude")),
            "longitude": float(row.get("longitude")),
            "altitude": float(row.get("altitude") or 0) if pd.notna(row.get("altitude")) else None,
        }

        # 可选字段
        if pd.notna(row.get("description")):
            station_data["description"] = str(row.get("description"))

        if existing:
            # 更新现有记录（保留原有station_id，更新其他信息）
            if pd.notna(row.get("latitude")):
                existing.latitude = float(row.get("latitude"))
            if pd.notna(row.get("longitude")):
                existing.longitude = float(row.get("longitude"))
            if pd.notna(row.get("altitude")):
                existing.altitude = float(row.get("altitude"))
            if pd.notna(row.get("description")):
                existing.description = str(row.get("description"))
            updated_count += 1
        else:
            # 插入新记录
            new_station = RadarStation(**station_data)
            db.add(new_station)
            inserted_count += 1

        row_count += 1

        # 每处理一条记录发送一次进度
        progress = 30.0 + (row_count / total_rows * 50)
        if idx % 5 == 0 or idx == total_rows - 1:  # 减少通知频率
            send_ws_notification({
                "type": "progress",
                "file_id": file_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "status": "processing",
                    "progress": progress,
                    "stage": "存储中",
                    "processed_rows": row_count,
                    "total_rows": total_rows,
                    "message": f"正在处理雷达站配置... ({row_count}/{total_rows})"
                }
            })

    db.commit()

    # 更新文件状态
    db_file = db.query(DataFile).filter(DataFile.id == file_id).first()
    db_file.row_count = row_count
    db_file.status = "completed"
    db_file.processed_time = datetime.utcnow()
    db.commit()

    # 通知：处理完成
    send_ws_notification({
        "type": "completed",
        "file_id": file_id,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "status": "completed",
            "progress": 100.0,
            "stage": "完成",
            "processed_rows": row_count,
            "total_rows": row_count,
            "message": f"处理完成：新增 {inserted_count} 个，更新 {updated_count} 个"
        }
    })

    return {
        "row_count": row_count,
        "inserted": inserted_count,
        "updated": updated_count,
        "message": f"雷达站配置处理完成：新增 {inserted_count} 个，更新 {updated_count} 个"
    }


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
    """删除文件（从 MinIO 和数据库）"""
    db_file = db.query(DataFile).filter(
        DataFile.id == file_id,
        DataFile.user_id == user_id
    ).first()

    if not db_file:
        return False

    # 从 MinIO 删除文件
    try:
        minio_service.delete_file(db_file.file_path)
    except Exception as e:
        # 记录错误但继续删除数据库记录
        from core.logging import get_logger
        logger = get_logger(__name__)
        logger.warning(f"MinIO 文件删除失败，继续删除数据库记录: {e}")

    # 删除关联的轨迹数据（按依赖顺序：先删 FlightTrackRaw，再删 RadarStation）
    db.query(FlightTrackRaw).filter(FlightTrackRaw.file_id == file_id).delete(synchronize_session=False)
    db.query(RadarStation).filter(RadarStation.file_id == file_id).delete(synchronize_session=False)

    # 删除数据库记录
    db.delete(db_file)
    db.commit()
    return True
