"""
SMTP 邮箱服务测试脚本
用于测试邮箱配置是否正常，并可选发送测试邮件
"""
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    VERIFICATION_CODE_LENGTH,
    VERIFICATION_CODE_EXPIRE_MINUTES,
    LOG_VERIFICATION_CODE,
)


def test_connection():
    """测试 SMTP 连接"""
    print("\n" + "=" * 50)
    print("测试 SMTP 连接")
    print("=" * 50)

    if not SMTP_HOST or not SMTP_PORT:
        print("[ERROR] SMTP_HOST 或 SMTP_PORT 未配置")
        return False

    if not SMTP_USER or not SMTP_PASSWORD:
        print("[ERROR] SMTP_USER 或 SMTP_PASSWORD 未配置")
        return False

    print(f"SMTP 服务器: {SMTP_HOST}")
    print(f"SMTP 端口: {SMTP_PORT}")
    print(f"发件邮箱: {SMTP_USER}")

    try:
        # 根据端口选择加密方式
        if SMTP_PORT == 465:
            # SSL 加密
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
            print(f"[INFO] 使用 SSL 加密连接 (端口 {SMTP_PORT})")
        else:
            # STARTTLS 加密 (端口 587 或 25)
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            print(f"[INFO] 使用 STARTTLS 加密连接 (端口 {SMTP_PORT})")
            server.starttls()

        # 登录测试
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("[OK] SMTP 连接成功")
        print("[OK] 邮箱登录成功")

        server.quit()
        return True

    except smtplib.SMTPAuthenticationError:
        print("[ERROR] 邮箱认证失败")
        print("[HINT] 请检查邮箱账号和密码/授权码是否正确")
        print("[HINT] 部分邮箱服务需要使用「授权码」而非登录密码")
        return False

    except smtplib.SMTPConnectError as e:
        print(f"[ERROR] 无法连接到 SMTP 服务器: {e}")
        print("[HINT] 请检查 SMTP_HOST 和 SMTP_PORT 是否正确")
        print("[HINT] 请检查网络连接是否正常")
        return False

    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP 错误: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] 未知错误: {e}")
        return False


def send_test_email(to_email: str):
    """发送测试邮件"""
    print("\n" + "=" * 50)
    print(f"发送测试邮件到: {to_email}")
    print("=" * 50)

    try:
        # 根据端口选择加密方式
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()

        server.login(SMTP_USER, SMTP_PASSWORD)

        # 构建邮件
        msg = MIMEMultipart()
        msg['From'] = formataddr(("RFTIP 智能雷达轨迹分析平台", SMTP_USER))
        msg['To'] = to_email
        msg['Subject'] = "RFTIP 邮箱服务测试"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">RFTIP 邮箱服务测试</h2>
                <p>这是一封来自 <strong>RFTIP 智能雷达轨迹分析平台</strong> 的测试邮件。</p>
                <p>如果您收到此邮件，说明邮箱服务配置正确！</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #888; font-size: 12px;">
                    SMTP 服务器: {SMTP_HOST}<br>
                    SMTP 端口: {SMTP_PORT}<br>
                    发件邮箱: {SMTP_USER}
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # 发送邮件
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
        print(f"[OK] 测试邮件发送成功")

        server.quit()
        return True

    except Exception as e:
        print(f"[ERROR] 发送测试邮件失败: {e}")
        return False


def show_config():
    """显示当前邮箱配置"""
    print("\n" + "=" * 50)
    print("当前邮箱配置")
    print("=" * 50)
    print(f"SMTP_HOST: {SMTP_HOST}")
    print(f"SMTP_PORT: {SMTP_PORT}")
    print(f"SMTP_USER: {SMTP_USER}")
    print(f"SMTP_PASSWORD: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else '(未配置)'}")
    print(f"VERIFICATION_CODE_LENGTH: {VERIFICATION_CODE_LENGTH}")
    print(f"VERIFICATION_CODE_EXPIRE_MINUTES: {VERIFICATION_CODE_EXPIRE_MINUTES}")
    print(f"LOG_VERIFICATION_CODE: {LOG_VERIFICATION_CODE}")


def main():
    """主函数"""
    print("=" * 50)
    print("RFTIP 邮箱服务测试")
    print("=" * 50)

    # 显示配置
    show_config()

    # 测试连接
    connection_ok = test_connection()

    # 询问是否发送测试邮件
    if connection_ok:
        print("\n" + "=" * 50)
        send_test = input("是否发送测试邮件? (输入收件邮箱地址或直接回车跳过): ").strip()

        if send_test:
            if "@" in send_test and "." in send_test:
                send_test_email(send_test)
            else:
                print("[WARN] 邮箱格式不正确，跳过发送测试邮件")
    else:
        print("\n" + "=" * 50)
        print("[WARN] SMTP 连接失败，跳过发送测试邮件")

    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    print(f"SMTP 连接: {'✓ 成功' if connection_ok else '✗ 失败'}")
    print("=" * 50)

    if connection_ok:
        print("[OK] 邮箱服务配置正常！")
    else:
        print("[ERROR] 邮箱服务配置有误，请检查配置")
    print("=" * 50)

    return 0 if connection_ok else 1


if __name__ == "__main__":
    exit(main())
