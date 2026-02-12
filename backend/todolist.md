# RFTIP 后端配置待办清单

## 邮箱验证码功能配置

### 1. 获取邮箱授权码

根据你使用的邮箱，按以下步骤获取授权码：

#### QQ 邮箱
1. 登录 QQ 邮箱网页版
2. 点击「设置」→「账户」
3. 找到「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
4. 开启「IMAP/SMTP服务」
5. 生成授权码（不是 QQ 密码！）

#### 163 邮箱
1. 登录 163 邮箱网页版
2. 点击「设置」→「POP3/SMTP/IMAP」
3. 开启「IMAP/SMTP服务」
4. 发送短信验证后获取授权码

#### Gmail
1. 开启两步验证
2. 进入 Google 账户安全设置
3. 生成「应用专用密码」

---

### 2. 创建并配置 .env 文件

在 `backend` 目录下创建 `.env` 文件，填入以下内容：

```env
# 数据库配置（建议修改默认密码）
DATABASE_URL=mysql+pymysql://root:your_new_password@localhost:3306/rftip_db

# JWT 密钥（生产环境务必更换）
SECRET_KEY=your-random-secret-key-at-least-32-characters-long

# SMTP 邮件配置
SMTP_ENABLED=true
SMTP_HOST=smtp.qq.com           # 根据你的邮箱服务商填写
SMTP_PORT=587                 # SSL 用 465，TLS 用 587
SMTP_FROM=your@qq.com          # 你的邮箱地址
SMTP_USER=your@qq.com          # SMTP 登录账号（通常与邮箱相同）
SMTP_PASSWORD=your_auth_code    # 填入第 1 步获取的授权码
SMTP_FROM_NAME=RFTIP 系统

# 验证码配置（可选，有默认值）
VERIFICATION_CODE_EXPIRE_MINUTES=5
VERIFICATION_CODE_LENGTH=6
LOG_VERIFICATION_CODE=true
```

---

### 3. 验证配置

启动后端服务：
```bash
cd backend
python main.py
```

调用发送验证码接口测试：
```bash
curl -X POST http://localhost:8000/api/auth/send-verification-code \
  -H "Content-Type: application/json" \
  -d '{"email": "your@qq.com"}'
```

检查控制台是否打印验证码：
```
==================================================
📧 验证码已生成
邮箱: your@qq.com
验证码: 123456
有效期: 5 分钟
过期时间: 2024-02-12 15:30:00
==================================================
```

---

### 4. 测试注册流程

1. 调用 `/api/auth/send-verification-code` 获取验证码
2. 从控制台或邮箱获取 6 位验证码
3. 调用 `/api/auth/register` 完成注册：
```json
{
  "username": "testuser",
  "email": "your@qq.com",
  "password": "123456",
  "verification_code": "123456"
}
```

---

## 可选优化项

- [ ] 将验证码存储从内存改为 Redis（生产环境推荐）
- [ ] 添加验证码发送频率限制（防刷）
- [ ] 完善邮件模板样式
- [ ] 添加「忘记密码」邮件验证功能
