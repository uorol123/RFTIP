"""
邮件服务模块
负责发送验证码邮件
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Optional
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """邮件服务类"""

    def __init__(self):
        self.enabled = settings.smtp_enabled
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_from = settings.smtp_from
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from_name = settings.smtp_from_name
        self.use_tls = settings.smtp_use_tls

    def send_verification_code(self, to_email: str, code: str) -> bool:
        """
        发送验证码邮件

        Args:
            to_email: 收件人邮箱
            code: 验证码

        Returns:
            bool: 发送是否成功
        """
        if not self.enabled:
            logger.warning("邮件发送功能已禁用，但验证码已生成")
            return True

        if not all([self.smtp_host, self.smtp_from, self.smtp_user, self.smtp_password]):
            logger.error("SMTP 配置不完整，无法发送邮件")
            return False

        try:
            # 创建邮件
            message = MIMEMultipart("alternative")
            message["Subject"] = f"{self.smtp_from_name} - 邮箱验证码"
            message["From"] = formataddr((self.smtp_from_name, self.smtp_user))
            message["To"] = to_email

            # 邮件内容（HTML 格式）
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .code-box {{ background: white; border: 2px dashed #667eea; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; margin: 20px 0; border-radius: 5px; }}
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 15px 0; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>{self.smtp_from_name}</h2>
                        <p>邮箱验证码</p>
                    </div>
                    <div class="content">
                        <p>您好，</p>
                        <p>您正在进行邮箱验证，验证码如下：</p>
                        <div class="code-box">{code}</div>
                        <div class="warning">
                            <strong>⚠️ 重要提示：</strong>
                            <ul style="margin: 10px 0; padding-left: 20px;">
                                <li>验证码有效期为 <strong>{settings.verification_code_expire_minutes} 分钟</strong></li>
                                <li>请勿将验证码告诉他人</li>
                                <li>如非本人操作，请忽略此邮件</li>
                            </ul>
                        </div>
                    </div>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿直接回复</p>
                        <p>&copy; 2026 {self.smtp_from_name}. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # 连接 SMTP 服务器并发送
            if self.smtp_port == 465:
                # 端口 465 使用 SSL
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)
            else:
                # 其他端口使用 STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(message)

            logger.info(f"验证码邮件已发送至: {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP 认证失败: {e}")
            logger.error("请检查邮箱账号和授权码是否正确")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP 发送失败: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送异常: {e}")
            return False


# 全局邮件服务实例
email_service = EmailService()
