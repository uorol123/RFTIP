"""
认证服务 - 处理用户认证相关业务逻辑
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import get_settings
from app.models.user import User, UserLoginLog
from app.schemas.auth import UserCreate, TokenData, UserUpdate

settings = get_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """加密密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, username=username)
    except JWTError:
        return None


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """通过用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """通过邮箱获取用户"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """通过用户ID获取用户"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """创建新用户"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """验证用户身份"""
    # 支持用户名或邮箱登录
    user = get_user_by_username(db, username)
    if not user:
        user = get_user_by_email(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def create_login_log(
    db: Session,
    user_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "success",
    failure_reason: Optional[str] = None,
) -> UserLoginLog:
    """创建登录日志"""
    log = UserLoginLog(
        user_id=user_id,
        login_time=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent,
        login_status=status,
        failure_reason=failure_reason,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_logout_time(db: Session, log_id: int) -> Optional[UserLoginLog]:
    """更新登出时间"""
    log = db.query(UserLoginLog).filter(UserLoginLog.id == log_id).first()
    if log:
        log.logout_time = datetime.utcnow()
        db.commit()
        db.refresh(log)
    return log


def get_user_login_logs(db: Session, user_id: int, limit: int = 10) -> list[UserLoginLog]:
    """获取用户登录日志"""
    return (
        db.query(UserLoginLog)
        .filter(UserLoginLog.user_id == user_id)
        .order_by(UserLoginLog.login_time.desc())
        .limit(limit)
        .all()
    )
