# 🚀 GitHub上传 - 网页版指南（无需下载）

## ✅ 最简单的方法：直接在GitHub网页创建文件

由于下载链接无法访问，我们使用**更简单的方法**：直接在GitHub网页上创建文件！

---

## 📝 方法：在GitHub网页上逐个创建重要文件

### 第1步：访问您的仓库

```
https://github.com/turekent/Industry-Crisis-Advisor-
```

---

### 第2步：创建 README.md（项目说明）

1. 点击 **"Add file" → "Create new file"**
2. 文件名输入：`README.md`
3. 粘贴以下内容：

```markdown
# 🛡️ 产业避险参谋 (Industry Risk Advisor)

基于AI的战争动态成本预警系统，为六大行业提供实时风险分析和采购建议。

## 🎯 功能特点

- 📰 **实时市场动态**：自动抓取彭博社、路透社等权威来源
- 💰 **核心价格指标**：监控原油、铜、铝、钯金、黄金、SCFI运费
- 🔍 **行业风险查询**：支持PCB、游艇、生物医药、新型储能、打印耗材、跨境电商
- 📊 **成本影响分析**：AI自动计算战争动态对成本的影响
- 💡 **决策建议**：提供真金白银的采购建议

## 🛠️ 技术栈

- **后端**: Python (FastAPI, LangChain, LangGraph)
- **前端**: HTML/CSS/JavaScript
- **AI**: 豆包大模型 (doubao-seed-1-8-251228)
- **搜索**: coze-coding-dev-sdk

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入您的API密钥
```

### 启动服务

```bash
python src/main.py
```

### 访问界面

```
http://localhost:5000/static/realtime_index_enhanced.html
```

## 📁 项目结构

```
.
├── src/                    # 源代码
│   ├── agents/            # Agent代码
│   ├── tools/             # 工具代码
│   ├── api_routes.py      # API路由
│   └── main.py            # 主服务
├── assets/                 # 静态资源
│   └── realtime_index_enhanced.html
├── config/                 # 配置文件
├── README.md              # 项目说明
└── requirements.txt       # 依赖列表
```

## 📊 在线演示

访问实时版界面查看效果。

## 📄 License

MIT License

## 👤 Author

Created by turekent
```

4. 点击 **"Commit new file"**

---

### 第3步：创建 requirements.txt（依赖列表）

1. 点击 **"Add file" → "Create new file"**
2. 文件名输入：`requirements.txt`
3. 粘贴以下内容：

```txt
fastapi>=0.109.0
uvicorn>=0.27.0
langchain>=0.1.0
langgraph>=0.0.20
langchain-openai>=0.0.5
coze-coding-dev-sdk>=1.0.0
coze-coding-utils>=1.0.0
pydantic>=2.0.0
python-multipart>=0.0.6
aiohttp>=3.9.0
```

4. 点击 **"Commit new file"**

---

### 第4步：创建 .gitignore

1. 点击 **"Add file" → "Create new file"**
2. 文件名输入：`.gitignore`
3. 粘贴以下内容：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# Environment Variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Cache
.cache/
*.cache
```

4. 点击 **"Commit new file"**

---

### 第5步：创建 .env.example

1. 点击 **"Add file" → "Create new file"**
2. 文件名输入：`.env.example`
3. 粘贴以下内容：

```bash
# 环境变量配置示例
# 复制此文件为 .env 并填入您的实际配置

# Coze API配置
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn

# 服务配置
SERVICE_PORT=5000
SERVICE_HOST=0.0.0.0
```

4. 点击 **"Commit new file"**

---

## 📁 创建文件夹和更多文件

### 创建 src 文件夹

1. 点击 **"Add file" → "Create new file"**
2. 文件名输入：`src/.gitkeep`（这会自动创建src文件夹）
3. 内容留空
4. 点击 **"Commit new file"**

### 创建 src/main.py

1. 点击 **"Add file" → "Create new file"**
2. 文件名输入：`src/main.py`
3. 粘贴以下内容（简化版）：

```python
"""
产业避险参谋 - 主服务
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="产业避险参谋")

# 挂载静态文件
WORKSPACE_PATH = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
assets_path = os.path.join(WORKSPACE_PATH, "assets")
if os.path.exists(assets_path):
    app.mount("/static", StaticFiles(directory=assets_path), name="static")

@app.get("/")
async def root():
    """首页"""
    return {"message": "产业避险参谋 API 服务运行中"}

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
```

4. 点击 **"Commit new file"**

---

## ✅ 完成！

按照以上步骤，您就在GitHub上创建了一个完整的项目结构！

---

## 💡 更进一步

如果您想上传更多代码文件（如API路由、前端页面等），我可以：

1. **提供完整代码内容**，您直接复制粘贴
2. **创建更多文件**，如 `src/api_routes.py`
3. **添加前端页面**，如 `assets/index.html`

---

## 📞 需要帮助？

告诉我您想创建哪个文件，我立即提供完整内容！

---

## 🎯 总结

**最简单的方法：**
1. 访问GitHub仓库
2. 点击 "Add file" → "Create new file"
3. 输入文件名，粘贴内容
4. 点击 "Commit new file"

**重复创建以下文件：**
- ✅ README.md
- ✅ requirements.txt
- ✅ .gitignore
- ✅ .env.example
- ✅ src/main.py

**总时间：10分钟**
