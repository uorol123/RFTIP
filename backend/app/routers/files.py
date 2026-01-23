"""
文件管理路由 - 处理文件上传、下载、删除等操作
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session

from core.database import get_db
from app.routers.auth import get_current_active_user, UserResponse
from app.schemas.file import (
    DataFileResponse,
    DataFileListResponse,
    FileUploadResponse,
)
from app.services import file_service

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    上传数据文件

    支持的格式: CSV, Excel (.xlsx, .xls)
    """
    return await file_service.save_uploaded_file(file, current_user.id, db)


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
