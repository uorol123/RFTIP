"""
测试 bcrypt 密码加密功能
验证与项目代码一致
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import bcrypt


def test_bcrypt_direct():
    """直接测试 bcrypt 库"""
    print("=" * 60)
    print("测试 1: 直接使用 bcrypt 库")
    print("=" * 60)

    password = "QWEzxc200348"
    print(f"原始密码: {password}")
    print(f"密码长度: {len(password)} 字符")
    print(f"UTF-8 字节数: {len(password.encode('utf-8'))} 字节")

    # 截断到 72 字节
    password_bytes = password.encode('utf-8')[:72]
    print(f"截断后字节数: {len(password_bytes)} 字节")

    # 生成 hash
    salt = bcrypt.gensalt()
    print(f"生成的 salt: {salt!r}")

    hashed = bcrypt.hashpw(password_bytes, salt)
    print(f"Hash 结果: {hashed!r}")
    print(f"Hash 长度: {len(hashed)} 字节")

    # 验证
    is_valid = bcrypt.checkpw(password_bytes, hashed)
    print(f"验证结果: {is_valid}")

    # 验证完整密码（不截断）
    full_bytes = password.encode('utf-8')
    is_valid_full = bcrypt.checkpw(full_bytes, hashed)
    print(f"验证完整密码: {is_valid_full}")

    print()
    return is_valid


def test_project_code():
    """测试项目中的 auth_service 代码"""
    print("=" * 60)
    print("测试 2: 使用项目中的 auth_service")
    print("=" * 60)

    from app.services.auth_service import get_password_hash, verify_password

    password = "QWEzxc200348"
    print(f"原始密码: {password}")

    # 生成 hash
    hashed = get_password_hash(password)
    print(f"Hash 结果: {hashed}")
    print(f"Hash 长度: {len(hashed)} 字符")

    # 验证
    is_valid = verify_password(password, hashed)
    print(f"验证结果: {is_valid}")

    # 验证错误密码
    is_wrong = verify_password("wrongpassword", hashed)
    print(f"验证错误密码: {is_wrong}")

    print()
    return is_valid and not is_wrong


def test_long_password():
    """测试长密码"""
    print("=" * 60)
    print("测试 3: 测试超过 72 字节的密码")
    print("=" * 60)

    from app.services.auth_service import get_password_hash, verify_password

    # 生成一个很长的密码
    long_password = "a" * 100
    print(f"长密码长度: {len(long_password)} 字符")
    print(f"UTF-8 字节数: {len(long_password.encode('utf-8'))} 字节")

    # 生成 hash
    hashed = get_password_hash(long_password)
    print(f"Hash 结果: {hashed}")

    # 验证完整密码
    is_valid = verify_password(long_password, hashed)
    print(f"验证完整长密码: {is_valid}")

    # 验证前 72 字节
    password_72 = long_password[:72]
    is_valid_72 = verify_password(password_72, hashed)
    print(f"验证前 72 字符: {is_valid_72}")

    # 验证前 71 字节（应该失败）
    password_71 = long_password[:71]
    is_valid_71 = verify_password(password_71, hashed)
    print(f"验证前 71 字符: {is_valid_71}")

    print()
    return is_valid and is_valid_72 and not is_valid_71


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("bcrypt 密码加密测试")
    print("=" * 60)

    results = []

    try:
        results.append(("直接 bcrypt 测试", test_bcrypt_direct()))
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        results.append(("直接 bcrypt 测试", False))

    try:
        results.append(("项目代码测试", test_project_code()))
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        results.append(("项目代码测试", False))

    try:
        results.append(("长密码测试", test_long_password()))
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        results.append(("长密码测试", False))

    # 汇总结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("所有测试通过！")
        return 0
    else:
        print("部分测试失败！")
        return 1


if __name__ == "__main__":
    exit(main())
