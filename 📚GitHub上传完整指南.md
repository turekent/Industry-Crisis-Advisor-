# 📚 GitHub上传完整指南

## 🎯 目标

将"产业避险参谋"项目代码上传到GitHub

---

## 📝 步骤1: 在GitHub创建新仓库

### 1.1 登录GitHub

访问：https://github.com

### 1.2 创建新仓库

1. 点击右上角 **+** 号
2. 选择 **New repository**

### 1.3 填写仓库信息

```
Repository name: industry-risk-advisor
Description: 🛡️ 产业避险参谋 - 基于AI的战争动态成本预警系统
Visibility: ✅ Public（公开）或 Private（私有）

⚠️ 重要：不要勾选以下选项（因为本地已有代码）：
[ ] Add a README file
[ ] Add .gitignore
[ ] Choose a license
```

### 1.4 点击 **Create repository**

---

## 📝 步骤2: 连接远程仓库

创建成功后，GitHub会显示一个页面，选择 **"…or push an existing repository from the command line"**

### 方式A: 使用HTTPS（推荐新手）

```bash
cd /workspace/projects

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/industry-risk-advisor.git

# 推送代码
git push -u origin main
```

### 方式B: 使用SSH（推荐有经验用户）

```bash
cd /workspace/projects

# 添加远程仓库
git remote add origin git@github.com:YOUR_USERNAME/industry-risk-advisor.git

# 推送代码
git push -u origin main
```

**注意**：将 `YOUR_USERNAME` 替换为您的GitHub用户名

---

## 📝 步骤3: 验证上传成功

推送完成后，访问您的仓库页面：

```
https://github.com/YOUR_USERNAME/industry-risk-advisor
```

您应该能看到所有代码文件！

---

## 🔧 完整操作命令（复制粘贴即可）

### 如果您还没有提交最新代码：

```bash
# 1. 进入项目目录
cd /workspace/projects

# 2. 查看当前状态
git status

# 3. 添加所有新文件
git add .

# 4. 提交更改
git commit -m "feat: 实施系统稳定性增强，添加重试、超时、缓存机制"

# 5. 添加远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/industry-risk-advisor.git

# 6. 推送到GitHub
git push -u origin main
```

### 如果代码已经提交（当前状态）：

```bash
# 1. 进入项目目录
cd /workspace/projects

# 2. 添加远程仓库（替换YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/industry-risk-advisor.git

# 3. 推送到GitHub
git push -u origin main
```

---

## 🔐 身份验证问题

### 如果使用HTTPS推送时要求输入密码：

GitHub已不再支持密码认证，需要使用 **Personal Access Token (PAT)**

#### 创建Personal Access Token：

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 设置：
   - Note: `industry-risk-advisor`
   - Expiration: `No expiration` 或 `90 days`
   - Select scopes: ✅ 勾选 `repo`（完整仓库访问权限）
4. 点击 **Generate token**
5. **⚠️ 立即复制token（只显示一次）**

#### 使用token推送：

```bash
# 方式1: 在推送时输入token作为密码
git push -u origin main
# Username: YOUR_USERNAME
# Password: 粘贴您的token

# 方式2: 在URL中包含token（永久保存）
git remote set-url origin https://TOKEN@github.com/YOUR_USERNAME/industry-risk-advisor.git
git push -u origin main
```

---

## 🚀 后续更新代码

以后有新的代码更改，只需要：

```bash
# 1. 查看更改
git status

# 2. 添加更改
git add .

# 3. 提交更改
git commit -m "描述您的更改"

# 4. 推送到GitHub
git push
```

---

## 📊 项目文件结构（将上传的内容）

```
industry-risk-advisor/
├── 📁 src/                          # 源代码
│   ├── 📁 agents/                   # Agent代码
│   ├── 📁 tools/                    # 工具代码
│   ├── 📁 storage/                  # 存储代码
│   ├── 📁 utils/                    # 工具函数
│   ├── api_routes.py                # API路由
│   ├── api_routes_enhanced.py       # 增强版API路由
│   └── main.py                      # 主服务
├── 📁 assets/                       # 静态资源
│   ├── realtime_index.html          # 实时版页面
│   ├── realtime_index_enhanced.html # 增强版页面
│   └── test_api.html                # API测试页面
├── 📁 config/                       # 配置文件
├── 📄 README.md                     # 项目说明
├── 📄 requirements.txt              # 依赖列表
├── 📄 .gitignore                    # Git忽略文件
├── 📄 LICENSE                       # 开源协议
└── 📄 各种文档.md                    # 说明文档
```

---

## ✅ 检查清单

在上传前，请确认：

- [ ] 已在GitHub创建仓库
- [ ] 已安装Git（已安装✅）
- [ ] 已配置Git用户信息
- [ ] 已添加远程仓库
- [ ] 已推送代码

### 检查Git配置：

```bash
# 查看用户名和邮箱
git config user.name
git config user.email

# 如果未配置，设置一下：
git config --global user.name "您的名字"
git config --global user.email "your.email@example.com"
```

---

## 🆘 常见问题

### Q1: 推送时提示 "fatal: 'origin' already exists"

**解决**：
```bash
# 先删除旧的远程仓库
git remote remove origin

# 再添加新的
git remote add origin https://github.com/YOUR_USERNAME/industry-risk-advisor.git
```

### Q2: 推送时提示 "fatal: refusing to merge unrelated histories"

**解决**：
```bash
# 强制推送（如果确认远程仓库没有重要内容）
git push -u origin main --force

# 或者合并历史
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Q3: 如何查看远程仓库地址？

```bash
git remote -v
```

### Q4: 如何修改远程仓库地址？

```bash
# 方式1
git remote set-url origin https://github.com/YOUR_USERNAME/NEW_REPO.git

# 方式2
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/NEW_REPO.git
```

---

## 🎯 快速开始（3步完成）

```bash
# 步骤1: 添加远程仓库（替换YOUR_USERNAME）
cd /workspace/projects
git remote add origin https://github.com/YOUR_USERNAME/industry-risk-advisor.git

# 步骤2: 推送代码
git push -u origin main

# 步骤3: 输入GitHub用户名和token
# Username: YOUR_USERNAME
# Password: YOUR_PERSONAL_ACCESS_TOKEN
```

---

## 📞 需要帮助？

如果遇到任何问题，请告诉我：
1. 具体的错误信息
2. 您使用的操作系统
3. Git版本（运行 `git --version` 查看）

我会帮您解决！
