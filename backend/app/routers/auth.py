"""
认证路由 - 处理用户注册、登录、登出等操作
"""
from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File, Form, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.config import get_settings, REDIS_URL
from core.database import get_db
from core.logging import logger
from app.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    UserUpdate,
    LoginLogResponse,
    ChangePasswordRequest,
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
    AvatarUploadResponse,
    TempAvatarUploadResponse,
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
from app.services.minio_service import minio_service
from app.services.temp_avatar_service import temp_avatar_service

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


@router.post("/upload-temp-avatar", response_model=TempAvatarUploadResponse)
async def upload_temp_avatar(
    avatar: Annotated[UploadFile, File(description="头像文件")],
    request: Request,
):
    """
    上传临时头像（无需登录）

    用于注册前的头像上传

    - **avatar**: 头像文件（支持 jpg、png、gif 等图片格式）
    - 文件大小限制：5MB
    - 临时存储在 Redis，1 小时后自动过期
    - IP 限流：每分钟最多 3 次

    返回 temp_token，用于注册时传入
    """
    # 获取客户端 IP
    client_ip = request.client.host if request.client else "unknown"

    # IP 限流检查：每分钟最多 3 次
    try:
        import redis
        redis_client = redis.from_url(REDIS_URL)
        rate_limit_key = f"upload_limit:{client_ip}"

        # 增加计数器
        current_count = redis_client.incr(rate_limit_key)

        # 第一次设置时，添加 60 秒过期时间
        if current_count == 1:
            redis_client.expire(rate_limit_key, 60)

        # 检查是否超过限制
        if current_count > 3:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="上传过于频繁，请稍后再试",
            )

    except ImportError:
        # 如果没有 redis 库，跳过限流
        pass
    except Exception as e:
        # Redis 连接失败时记录日志，但允许继续
        logger.error(f"IP 限流检查失败: {e}")

    # 验证文件类型
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
    if avatar.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：{avatar.content_type}。支持的类型：jpg、png、gif、webp",
        )

    # 验证文件大小（5MB）
    MAX_FILE_SIZE = 5 * 1024 * 1024
    file_data = await avatar.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 5MB）",
        )

    try:
        # 保存到 Redis
        temp_token = temp_avatar_service.save_temp_avatar(
            file_data=file_data,
            content_type=avatar.content_type or "image/jpeg",
        )

        return TempAvatarUploadResponse(
            temp_token=temp_token,
            message="临时头像上传成功，请在一小时内完成注册",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"临时头像上传失败：{str(e)}",
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
    - **temp_token**: 临时头像令牌（可选，需要先调用上传临时头像接口）

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

    # 处理临时头像
    avatar_object_name = None
    if user_data.temp_token:
        # 从 Redis 获取临时头像
        temp_avatar_data = temp_avatar_service.get_temp_avatar(user_data.temp_token)
        if temp_avatar_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="临时头像不存在或已过期，请重新上传",
            )

        file_data, content_type = temp_avatar_data

        # 先创建用户（需要 user_id）
        user = create_user(db, user_data)

        try:
            # 上传到 MinIO
            avatar_object_name = minio_service.upload_avatar(
                file_data=file_data,
                filename="avatar.jpg",
                user_id=user.id,
            )

            # 更新用户头像
            user.avatar_url = avatar_object_name
            db.commit()
            db.refresh(user)

        except Exception as e:
            # 如果头像上传失败，仍然注册成功，只是没有头像
            logger.error(f"头像上传失败: {e}")

        # 删除 Redis 中的临时头像
        temp_avatar_service.delete_temp_avatar(user_data.temp_token)

        return UserResponse.model_validate(user)

    # 没有临时头像，直接创建用户
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


@router.post("/upload-avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    avatar: Annotated[UploadFile, File(description="头像文件")],
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    上传用户头像

    - **avatar**: 头像文件（支持 jpg、png、gif 等图片格式）
    - 文件大小限制：5MB

    返回 avatar_id，可用于注册或更新用户信息
    """
    # 验证文件类型
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
    if avatar.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型：{avatar.content_type}。支持的类型：jpg、png、gif、webp",
        )

    # 验证文件大小（5MB）
    MAX_FILE_SIZE = 5 * 1024 * 1024
    file_data = await avatar.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 5MB）",
        )

    try:
        # 上传到 MinIO，获取 object_name
        avatar_id = minio_service.upload_avatar(
            file_data=file_data,
            filename=avatar.filename or "avatar.jpg",
            user_id=current_user.id,
        )

        return AvatarUploadResponse(
            avatar_id=avatar_id,
            message="头像上传成功",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"头像上传失败：{str(e)}",
        )


@router.get("/avatar/{user_id}")
async def get_avatar(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    """
    获取用户头像

    返回头像图片文件
    """
    # 获取用户信息
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    if not user.avatar_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未设置头像",
        )

    try:
        # 从 MinIO 获取头像文件
        file_data, content_type = minio_service.get_avatar(user.avatar_url)
        return Response(content=file_data, media_type=content_type)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取头像失败：{str(e)}",
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
    full_name: Annotated[Optional[str], Form()] = None,
    phone: Annotated[Optional[str], Form()] = None,
    avatar: Annotated[Optional[UploadFile], File()] = None,
):
    """
    更新当前用户信息

    请求方式：multipart/form-data

    - **full_name**: 全名（可选）
    - **phone**: 电话号码（可选）
    - **avatar**: 头像文件（可选）

    注意：
    - 头像文件支持：jpg、png、gif、webp（最大 5MB）
    - 上传新头像会自动删除旧头像
    """
    # 构建更新数据
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if phone is not None:
        update_data["phone"] = phone

    # 处理头像上传
    if avatar is not None:
        # 验证文件类型
        allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"}
        if avatar.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型：{avatar.content_type}",
            )

        # 验证文件大小（5MB）
        MAX_FILE_SIZE = 5 * 1024 * 1024
        file_data = await avatar.read()
        if len(file_data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过限制（最大 5MB）",
            )

        try:
            # 删除旧头像（如果存在）
            if current_user.avatar_url:
                minio_service.delete_avatar(current_user.avatar_url)

            # 上传新头像
            avatar_id = minio_service.upload_avatar(
                file_data=file_data,
                filename=avatar.filename or "avatar.jpg",
                user_id=current_user.id,
            )
            update_data["avatar_url"] = avatar_id

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"头像上传失败：{str(e)}",
            )

    # 执行更新
    if update_data:
        user_update = UserUpdate(**update_data)
        updated_user = update_user(db, current_user.id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )
        return UserResponse.model_validate(updated_user)

    # 没有更新内容，返回原用户信息
    return current_user


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
