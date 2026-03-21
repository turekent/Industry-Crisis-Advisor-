# 🏠 本地部署完整指南

## 📋 前提条件

确保您的电脑已安装：
- Python 3.8+
- pip 包管理器

## 🚀 快速部署步骤

### 步骤1：下载项目代码

将以下文件下载到本地电脑的同一个文件夹中：

```
your-project/
├── src/
│   ├── main.py
│   ├── agents/
│   │   └── agent.py
│   ├── tools/
│   │   ├── industry_risk_search.py
│   │   ├── cost_calculator.py
│   │   └── market_news.py
│   └── storage/
│       └── memory/
│           └── memory_saver.py
├── config/
│   └── agent_llm_config.json
├── assets/
│   ├── index.html
│   └── industry_knowledge_base.json
└── requirements.txt
```

### 步骤2：安装依赖

在项目根目录创建 `requirements.txt` 文件：

```txt
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.1.0
langgraph==1.0.0
langchain-openai==0.0.2
coze-coding-dev-sdk
psycopg-pool
psycopg
pydantic
python-multipart
```

然后安装依赖：

```bash
pip install -r requirements.txt
```

### 步骤3：配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# Linux/Mac
export COZE_WORKLOAD_IDENTITY_API_KEY="your_api_key"
export COZE_INTEGRATION_MODEL_BASE_URL="your_base_url"
export COZE_WORKSPACE_PATH="/path/to/your/project"

# Windows (PowerShell)
$env:COZE_WORKLOAD_IDENTITY_API_KEY="your_api_key"
$env:COZE_INTEGRATION_MODEL_BASE_URL="your_base_url"
$env:COZE_WORKSPACE_PATH="C:\path\to\your\project"
```

### 步骤4：启动服务

```bash
cd src
python main.py -m http -p 5000
```

### 步骤5：访问界面

打开浏览器，访问：
```
http://localhost:5000
```

## 📁 完整文件结构

如果您需要完整的项目文件，请参考以下结构：

```
/workspace/projects/
├── src/
│   ├── main.py                           # 主入口
│   ├── agents/
│   │   └── agent.py                      # Agent 核心代码
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── industry_risk_search.py       # 行业搜索工具
│   │   ├── cost_calculator.py            # 成本计算工具
│   │   └── market_news.py                # 市场新闻工具
│   ├── storage/
│   │   ├── __init__.py
│   │   └── memory/
│   │       ├── __init__.py
│   │       └── memory_saver.py           # 记忆管理
│   └── utils/                            # 工具函数
├── config/
│   └── agent_llm_config.json             # 模型配置
├── assets/
│   ├── index.html                         # 前端界面
│   └── industry_knowledge_base.json       # 知识库
├── requirements.txt                       # 依赖列表
└── README.md                              # 说明文档
```

## ⚠️ 常见问题

### 问题1：端口被占用

**错误信息**：`Address already in use`

**解决方案**：使用其他端口
```bash
python main.py -m http -p 8080
```

### 问题2：缺少依赖

**错误信息**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：安装缺失的依赖
```bash
pip install xxx
```

### 问题3：API密钥无效

**错误信息**：`Invalid API key`

**解决方案**：
1. 检查环境变量是否设置正确
2. 确认API密钥是否有效

### 问题4：数据库连接失败

**错误信息**：`Database connection failed`

**解决方案**：
- 系统会自动降级为内存存储，不影响使用
- 如需持久化，配置PostgreSQL数据库

## 🔧 简化部署（仅前端）

如果您只想查看前端界面，不需要后端功能：

### 方式一：直接打开HTML文件
```bash
# 使用浏览器打开
demo_standalone.html
```

### 方式二：使用简单的HTTP服务器
```bash
# Python 3
cd /workspace/projects/assets
python -m http.server 8000

# 然后访问
http://localhost:8000
```

## 📞 获取帮助

如果遇到问题：
1. 查看日志文件：`/app/work/logs/bypass/app.log`
2. 检查服务状态：`curl http://localhost:5000/health`
3. 查看文档：`README_WEB_INTERFACE.md`

## ✅ 验证部署成功

运行以下命令测试：

```bash
# 测试健康检查
curl http://localhost:5000/health

# 预期输出：{"status":"ok","message":"Service is running"}

# 测试市场新闻API
curl http://localhost:5000/market_news

# 预期输出：包含新闻列表的JSON数据
```

---

**🎉 部署完成后，即可在浏览器中访问 http://localhost:5000 使用完整功能！**
