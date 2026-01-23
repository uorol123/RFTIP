"""
认证路由 - 处理用户注册、登录、登出等操作
"""
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.config import get_settings
from core.database import get_db
from app.schemas.auth import UserCreate, UserResponse, Token, UserUpdate, LoginLogResponse
from app.services import (
    create_user,
    authenticate_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    create_access_token,
    create_login_log,
    update_logout_time,
    get_user_login_logs,
    update_user,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
settings = get_settings()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """获取当前登录用户"""
    from app.services import decode_access_token

    token_data = decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_id(db, token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    return UserResponse.model_validate(user)


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> UserResponse:
    """获取当前激活用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    """
    用户注册

    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少6字符）
    - **full_name**: 全名（可选）
    - **phone**: 电话号码（可选）
    """
    # 检查用户名是否已存在
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )

    # 检查邮箱是否已存在
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )

    # 创建用户
    user = create_user(db, user_data)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    user_agent: Annotated[str | None, Header()] = None,
    x_forwarded_for: Annotated[str | None, Header()] = None,
):
    """
    用户登录

    - **username**: 用户名或邮箱
    - **password**: 密码

    返回 JWT Token
    """
    # 验证用户
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # 记录失败日志（尝试获取用户ID）
        failed_user = get_user_by_username(db, form_data.username)
        if not failed_user:
            failed_user = get_user_by_email(db, form_data.username)
        if failed_user:
            create_login_log(
                db,
                user_id=failed_user.id,
                ip_address=x_forwarded_for,
                user_agent=user_agent,
                status="failed",
                failure_reason="用户名或密码错误",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 创建 Token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )

    # 记录登录日志
    create_login_log(
        db,
        user_id=user.id,
        ip_address=x_forwarded_for,
        user_agent=user_agent,
        status="success",
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    用户登出

    客户端应删除存储的 Token
    """
    # 获取最近的登录日志并更新登出时间
    logs = get_user_login_logs(db, current_user.id, limit=1)
    if logs:
        update_logout_time(db, logs[0].id)

    return {"message": "登出成功"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)]
):
    """
    获取当前用户信息
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    更新当前用户信息

    - **full_name**: 全名（可选）
    - **phone**: 电话号码（可选）
    - **avatar_url**: 头像URL（可选）
    """
    updated_user = update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return UserResponse.model_validate(updated_user)


@router.get("/login-logs", response_model=list[LoginLogResponse])
async def get_logs(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = 10,
):
    """
    获取当前用户的登录日志

    - **limit**: 返回记录数量（默认10条）
    """
    logs = get_user_login_logs(db, current_user.id, limit=min(limit, 100))
    return [LoginLogResponse.model_validate(log) for log in logs]
