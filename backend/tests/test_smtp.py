"""
SMTP 邮箱连接测试脚本
验证 SMTP 邮箱服务器连接和邮件发送功能
"""
import sys
import ssl
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


def test_smtp_connection():
    """测试 SMTP 服务器连接"""
    print("\n" + "=" * 50)
    print("测试 SMTP 服务器连接")
    print("=" * 50)

    # 从配置读取
    smtp_host = SMTP_HOST
    smtp_port = SMTP_PORT
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD

    if not smtp_host:
        print("[ERROR] SMTP_HOST 未配置，请在 .env 文件中设置")
        return False

    if not smtp_user or not smtp_password:
        print("[ERROR] SMTP_USER 或 SMTP_PASSWORD 未配置")
        return False

    print(f"SMTP 服务器: {smtp_host}:{smtp_port}")
    print(f"发件人邮箱: {smtp_user}")

    try:
        # 创建 SMTP 连接
        if smtp_port == 465:
            # SSL 连接
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=10)
        else:
            # STARTTLS 连接
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)

        # 如果是 STARTTLS 端口，启用 TLS
        if smtp_port == 587:
            context = ssl.create_default_context()
            server.starttls(context=context)

        # 登录
        server.login(smtp_user, smtp_password)

        print("[OK] SMTP 服务器连接成功")
        print("[OK] 邮箱登录认证成功")

        server.quit()
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] 邮箱认证失败: {e}")
        print("[HINT] 请检查 SMTP_USER 和 SMTP_PASSWORD 是否正确")
        print("[HINT] 注意：SMTP_PASSWORD 应该是授权码，不是登录密码")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"[ERROR] 无法连接到 SMTP 服务器: {e}")
        print("[HINT] 请检查 SMTP_HOST 和 SMTP_PORT 是否正确")
        return False
    except Exception as e:
        print(f"[ERROR] SMTP 连接失败: {e}")
        return False


def send_test_email(recipient_email=None):
    """发送测试邮件"""
    print("\n" + "=" * 50)
    print("发送测试邮件")
    print("=" * 50)

    # 从配置读取
    smtp_host = SMTP_HOST
    smtp_port = SMTP_PORT
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD

    # 如果没有指定收件人，使用发件人自己
    if not recipient_email:
        recipient_email = smtp_user
        print(f"未指定收件人，将发送测试邮件到发件人邮箱: {recipient_email}")

    print(f"收件人: {recipient_email}")

    try:
        # 创建邮件内容
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "RFTIP 系统 - SMTP 测试邮件"
        msg['From'] = smtp_user
        msg['To'] = recipient_email

        # 纯文本内容
        text_content = """
您好！

这是一封来自 RFTIP 系统的测试邮件。

如果您收到这封邮件，说明 SMTP 邮箱配置正确，可以正常发送邮件。

--
RFTIP 系统
"""

        # HTML 内容
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }
        .header h1 { color: white; margin: 0; font-size: 24px; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }
        .success { color: #28a745; font-weight: bold; }
        .footer { margin-top: 20px; font-size: 12px; color: #666; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>RFTIP 系统</h1>
        </div>
        <div class="content">
            <p>您好！</p>
            <p class="success">这是一封测试邮件，您的 SMTP 配置工作正常！</p>
            <p>邮件发送时间：""" + str(__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + """</p>
            <hr>
            <p>如果您收到这封邮件，说明：</p>
            <ul>
                <li>SMTP 服务器连接正常</li>
                <li>邮箱认证成功</li>
                <li>可以正常发送系统邮件</li>
            </ul>
        </div>
        <div class="footer">
            <p>此邮件由 RFTIP 系统自动发送，请勿回复</p>
        </div>
    </div>
</body>
</html>
"""

        # 添加邮件内容
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)

        # 发送邮件
        if smtp_port == 465:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            if smtp_port == 587:
                context = ssl.create_default_context()
                server.starttls(context=context)

        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, recipient_email, msg.as_string())
        server.quit()

        print("[OK] 测试邮件发送成功！")
        print(f"[INFO] 请检查收件箱: {recipient_email}")
        return True

    except Exception as e:
        print(f"[ERROR] 发送测试邮件失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("RFTIP SMTP 邮箱连接测试")
    print("=" * 50)
    print(f"项目路径: {project_root}")

    # 第一步：测试连接
    connection_ok = test_smtp_connection()

    if not connection_ok:
        print("\n" + "=" * 50)
        print("[ERROR] SMTP 连接测试失败")
        print("=" * 50)
        return 1

    # 第二步：询问是否发送测试邮件
    print("\n" + "-" * 50)
    response = input("是否发送测试邮件? (y/n): ").strip().lower()

    if response in ('y', 'yes', '是'):
        recipient = input("请输入收件人邮箱 (直接回车使用发件人): ").strip()
        recipient = recipient if recipient else None

        send_success = send_test_email(recipient)

        if send_success:
            print("\n" + "=" * 50)
            print("[OK] SMTP 测试完成，请检查收件箱")
            print("=" * 50)
            return 0
        else:
            print("\n" + "=" * 50)
            print("[ERROR] 发送测试邮件失败")
            print("=" * 50)
            return 1
    else:
        print("\n跳过发送测试邮件")
        print("=" * 50)
        print("[OK] SMTP 连接测试通过")
        print("=" * 50)
        return 0


if __name__ == "__main__":
    import datetime
    exit(main())
