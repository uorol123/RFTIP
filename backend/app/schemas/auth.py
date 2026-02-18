"""
认证相关的 Pydantic 模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, computed_field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")


class UserCreate(UserBase):
    """用户注册请求模型"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    verification_code: str = Field(..., min_length=6, max_length=6, description="邮箱验证码")
    temp_token: Optional[str] = Field(None, max_length=100, description="临时头像令牌")


class SendVerificationCodeRequest(BaseModel):
    """发送验证码请求模型"""
    email: EmailStr = Field(..., description="邮箱地址")


class SendVerificationCodeResponse(BaseModel):
    """发送验证码响应模型"""
    message: str
    email: str
    expire_in: int  # 剩余秒数


class AvatarUploadResponse(BaseModel):
    """头像上传响应模型"""
    avatar_id: str
    message: str


class TempAvatarUploadResponse(BaseModel):
    """临时头像上传响应模型"""
    temp_token: str
    message: str


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息更新模型"""
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = Field(..., min_length=6, max_length=50, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_active: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # 前端兼容字段
    @computed_field
    @property
    def is_admin(self) -> bool:
        return self.is_superuser

    @computed_field
    @property
    def avatar(self) -> Optional[str]:
        return self.avatar_url

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token 数据模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginLogResponse(BaseModel):
    """登录日志响应模型"""
    id: int
    user_id: int
    login_time: datetime
    logout_time: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_status: str
    failure_reason: Optional[str] = None

    class Config:
        from_attributes = True
