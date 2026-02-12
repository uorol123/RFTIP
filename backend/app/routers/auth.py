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
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    UserUpdate,
    LoginLogResponse,
    ChangePasswordRequest,
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
)
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
from app.services.email_service import email_service
from app.services.verification_service import verification_service

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


@router.post("/send-verification-code", response_model=SendVerificationCodeResponse)
async def send_verification_code(
    request: SendVerificationCodeRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    发送邮箱验证码

    - **email**: 邮箱地址

    注意：
    - 验证码有效期为 5 分钟
    - 每次发送会覆盖之前的验证码
    - 验证码会在日志中打印（方便测试）
    """
    email = request.email

    # 检查该邮箱是否已被注册
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )

    # 检查是否有未过期的验证码
    remaining_time = verification_service.get_remaining_time(email)
    if remaining_time is not None and remaining_time > 60:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"验证码已发送，请 {remaining_time // 60} 分钟后重试",
        )

    # 生成验证码
    code = verification_service.generate_code()
    verification_service.store_code(email, code)

    # 发送邮件
    email_sent = email_service.send_verification_code(email, code)

    # 计算过期时间
    from core.config import get_settings
    settings = get_settings()
    expire_in = settings.verification_code_expire_minutes * 60

    return SendVerificationCodeResponse(
        message="验证码已发送" if email_sent else "验证码已生成（邮件发送失败，请查看控制台）",
        email=email,
        expire_in=expire_in,
    )


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
    - **verification_code**: 邮箱验证码（6位数字）
    - **full_name**: 全名（可选）
    - **phone**: 电话号码（可选）

    注意：请先调用 /api/auth/send-verification-code 获取验证码
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

    # 验证邮箱验证码
    if not verification_service.verify_code(user_data.email, user_data.verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
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


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    修改当前用户密码

    - **old_password**: 旧密码
    - **new_password**: 新密码（至少6字符）
    """
    from app.services import verify_password, get_password_hash

    # 验证旧密码
    db_user = get_user_by_id(db, current_user.id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    if not verify_password(password_data.old_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误",
        )

    # 更新密码
    db_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "密码修改成功"}
