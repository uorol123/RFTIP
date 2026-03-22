"""
文件管理路由 - 处理文件上传、下载、删除等操作
"""
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.file import (
    DataFileResponse,
    DataFileListResponse,
    FileUploadResponse,
    DataFileUpdateVisibility,
    FileStatusResponse,
)
from app.services import file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    category: Annotated[str, Form()] = "trajectory",
):
    """
    上传数据文件（上传后自动处理）

    支持的格式: CSV, Excel (.xlsx, .xls)
    分类: trajectory（轨迹数据） / radar_station（雷达站配置）
    """
    import time
    route_start = time.time()

    # 保存文件
    upload_response = await file_service.save_uploaded_file(
        file, current_user.id, db, category
    )
    file_id = upload_response.file_id

    # 自动触发处理（异步）
    import asyncio
    asyncio.create_task(process_file_async(file_id, current_user.id, db))

    route_elapsed = time.time() - route_start
    print(f"[DEBUG] upload_file route handler elapsed: {route_elapsed:.3f}s", flush=True)

    return upload_response


async def process_file_async(file_id: int, user_id: int, db: Session):
    """
    异步处理文件（在线程池中执行，避免阻塞事件循环）
    """
    import asyncio
    import sys
    from core.database import SessionLocal
    from app.routers.websocket import manager as websocket_manager

    print(f"[DEBUG] Starting async file processing for file_id={file_id}", flush=True)

    # 创建新的数据库 session
    db_async = SessionLocal()

    try:
        # 验证文件存在且属于用户
        from app.services.file_service import get_file_by_id
        db_file = get_file_by_id(file_id, db_async, user_id)
        if not db_file:
            print(f"[ERROR] File {file_id} not found for user {user_id}", flush=True)
            return

        print(f"[DEBUG] File found: {db_file.file_name}, status: {db_file.status}", flush=True)

        # 处理文件（在线程池中执行，避免阻塞事件循环）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            file_service.process_file_data,
            file_id,
            db_async,
            websocket_manager,
            loop  # 传递 loop 用于线程安全的 WebSocket 通知
        )
        print(f"[DEBUG] File {file_id} processed successfully: {result}", flush=True)

    except Exception as e:
        import traceback
        print(f"[ERROR] Error processing file {file_id}: {e}", flush=True)
        traceback.print_exc()

        # 发送错误通知
        try:
            await websocket_manager.broadcast_to_file(file_id, {
                "type": "error",
                "file_id": file_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "status": "failed",
                    "message": str(e)
                }
            })
        except Exception as ws_error:
            print(f"[ERROR] Failed to send WebSocket error: {ws_error}", flush=True)

        # 尝试更新文件状态为失败
        try:
            from app.models.data_file import DataFile
            db_file = db_async.query(DataFile).filter(DataFile.id == file_id).first()
            if db_file:
                db_file.status = "failed"
                db_file.error_message = str(e)
                db_async.commit()
                print(f"[DEBUG] Updated file status to failed", flush=True)
        except Exception as update_error:
            print(f"[ERROR] Failed to update error status: {update_error}", flush=True)
    finally:
        db_async.close()
        print(f"[DEBUG] File processing task completed for file_id={file_id}", flush=True)


@router.post("/upload-batch", status_code=status.HTTP_201_CREATED)
async def upload_files_batch(
    files: Annotated[list[UploadFile], File()],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    category: Annotated[str, Form()] = "trajectory",
):
    """
    批量上传数据文件

    支持一次上传多个文件，每个文件会被单独处理
    """
    import asyncio
    import uuid

    # 生成批量任务ID
    task_id = str(uuid.uuid4())
    results = []

    # 上传所有文件
    for file in files:
        try:
            upload_response = await file_service.save_uploaded_file(
                file, current_user.id, db, category
            )
            file_id = upload_response.file_id

            # 异步处理每个文件
            asyncio.create_task(process_file_async(file_id, current_user.id, db))

            results.append({
                "filename": file.filename,
                "file_id": file_id,
                "status": "pending"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "file_id": None,
                "status": "failed",
                "error": str(e)
            })

    return {
        "task_id": task_id,
        "total_files": len(files),
        "files": results,
        "message": f"已成功上传 {len(results)} 个文件"
    }


@router.post("/{file_id}/process", response_model=dict)
async def process_file(
    file_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    处理上传的文件数据
    """
    # 验证文件所有权
    db_file = file_service.get_file_by_id(file_id, db, current_user.id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问",
        )

    try:
        result = file_service.process_file_data(file_id, db)
        return {
            "message": "文件处理成功",
            "file_id": file_id,
            **result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=DataFileListResponse)
async def list_files(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    获取当前用户的文件列表
    """
    files, total = file_service.get_user_files(db, current_user.id, skip, limit)
    return DataFileListResponse(
        total=total,
        files=[DataFileResponse.model_validate(f) for f in files]
    )


@router.get("/{file_id}", response_model=DataFileResponse)
async def get_file(
    file_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取文件详情
    """
    db_file = file_service.get_file_by_id(file_id, db, current_user.id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问",
        )
    return DataFileResponse.model_validate(db_file)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    删除文件
    """
    success = file_service.delete_file(file_id, db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权删除",
        )
    return None


@router.put("/{file_id}", response_model=DataFileResponse)
async def update_file_visibility(
    file_id: int,
    visibility_data: DataFileUpdateVisibility,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    更新文件可见性
    """
    db_file = file_service.get_file_by_id(file_id, db, current_user.id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问",
        )

    db_file.is_public = visibility_data.is_public
    db.commit()
    db.refresh(db_file)

    return DataFileResponse.model_validate(db_file)


@router.get("/{file_id}/status", response_model=FileStatusResponse)
async def get_file_status(
    file_id: int,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取文件处理状态
    """
    db_file = file_service.get_file_by_id(file_id, db, current_user.id)
    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在或无权访问",
        )

    # 计算处理进度和阶段
    progress = 0.0
    stage = None
    if db_file.status == "completed":
        progress = 100.0
        stage = "完成"
    elif db_file.status == "processing":
        progress = 50.0
        stage = "处理中"
    elif db_file.status == "pending":
        progress = 0.0
        stage = "待处理"
    elif db_file.status == "failed":
        progress = 0.0
        stage = "失败"

    return FileStatusResponse(
        file_id=db_file.id,
        filename=db_file.file_name,
        status=db_file.status,
        progress=progress,
        stage=stage,
        message=db_file.error_message if db_file.status == "failed" else None,
        processed_rows=db_file.row_count if db_file.row_count else 0,
        total_rows=db_file.row_count if db_file.row_count else 0,
    )
