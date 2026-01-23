"""
用户相关数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    """用户信息表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密后的密码")
    full_name = Column(String(100), comment="全名")
    phone = Column(String(20), comment="电话号码")
    avatar_url = Column(String(500), comment="头像URL")
    is_active = Column(Integer, default=1, comment="是否激活 (0:禁用, 1:激活)")
    is_superuser = Column(Integer, default=0, comment="是否超级管理员 (0:否, 1:是)")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    login_logs = relationship("UserLoginLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class UserLoginLog(Base):
    """用户登录日志表"""
    __tablename__ = "user_login_logs"

    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    login_time = Column(DateTime, default=datetime.utcnow, comment="登录时间")
    logout_time = Column(DateTime, comment="登出时间")
    ip_address = Column(String(50), comment="IP地址")
    user_agent = Column(String(500), comment="用户代理")
    login_status = Column(String(20), default="success", comment="登录状态 (success/failed)")
    failure_reason = Column(String(200), comment="失败原因")

    # 关系
    user = relationship("User", back_populates="login_logs")

    def __repr__(self):
        return f"<UserLoginLog(id={self.id}, user_id={self.user_id}, status='{self.login_status}')>"
