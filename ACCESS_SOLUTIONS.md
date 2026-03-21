# 🎯 2026 产业避险参谋长 - 访问指南

## 当前状态

✅ **服务已启动**：运行在端口 5000
✅ **后端API正常**：健康检查通过
✅ **前端界面就绪**：HTML文件已生成

---

## 🌐 三种访问方式

### 方式一：查看演示版（推荐新手）⭐

**适用场景**：只想查看界面效果，不需要真实数据

**操作步骤**：
1. 下载文件：`demo_standalone.html`
2. 用浏览器打开（双击文件）
3. 查看界面布局和演示数据

**优点**：
- ✅ 无需安装任何依赖
- ✅ 可以离线查看
- ✅ 快速了解界面功能

**注意**：
- ⚠️ 不会连接真实的API
- ⚠️ 显示的是模拟数据

---

### 方式二：本地部署完整服务（推荐开发者）⭐⭐⭐

**适用场景**：需要使用完整功能，有真实数据分析需求

**操作步骤**：

#### 1. 准备环境
```bash
# 确保已安装 Python 3.8+
python --version

# 创建项目目录
mkdir industry-risk-advisor
cd industry-risk-advisor
```

#### 2. 复制文件
将以下文件复制到本地：
- `src/` 目录下的所有文件
- `config/` 目录下的所有文件
- `assets/` 目录下的所有文件
- `requirements.txt`

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
# Linux/Mac
export COZE_WORKLOAD_IDENTITY_API_KEY="your_api_key_here"
export COZE_INTEGRATION_MODEL_BASE_URL="https://api.coze.cn"

# Windows
set COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
set COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn
```

#### 5. 启动服务
```bash
cd src
python main.py -m http -p 5000
```

#### 6. 访问界面
打开浏览器，访问：`http://localhost:5000`

**优点**：
- ✅ 完整功能
- ✅ 真实数据分析
- ✅ 可以自定义修改

**缺点**：
- ❌ 需要配置API密钥
- ❌ 需要安装依赖

---

### 方式三：使用当前环境（适用于有端口转发的平台）

**适用场景**：在支持端口转发的云平台或IDE环境中

**操作步骤**：

1. **查看平台文档**
   - 查找"端口转发"、"预览"或"Web服务"功能
   - 通常在控制台或预览面板中

2. **配置端口转发**
   - 源端口：5000
   - 目标端口：自动分配或自定义

3. **访问界面**
   - 使用平台提供的预览链接
   - 格式通常为：`https://your-workspace-id.preview.platform.com`

**优点**：
- ✅ 无需本地部署
- ✅ 使用已有的后端服务

**注意**：
- ⚠️ 需要平台支持端口转发功能
- ⚠️ 可能有网络延迟

---

## 📁 文件清单

### 演示文件
- `demo_standalone.html` - 独立演示版（可离线查看）
- `demo.html` - 依赖后端API的版本

### 完整项目文件
- `src/main.py` - 服务主入口
- `src/agents/agent.py` - Agent核心代码
- `src/tools/*.py` - 工具代码
- `config/agent_llm_config.json` - 模型配置
- `assets/index.html` - 前端界面
- `assets/industry_knowledge_base.json` - 知识库数据

### 文档文件
- `README_INDUSTRY_RISK_ADVISOR.md` - Agent功能说明
- `README_WEB_INTERFACE.md` - Web界面使用说明
- `LOCAL_DEPLOYMENT_GUIDE.md` - 本地部署指南
- `QUICK_START_GUIDE.md` - 快速启动指南

---

## 🧪 快速测试

### 测试后端API
```bash
# 健康检查
curl http://localhost:5000/health

# 获取市场新闻
curl http://localhost:5000/market_news | python -m json.tool | head -30

# 测试行业查询
curl -X POST http://localhost:5000/run \
  -H "Content-Type: application/json" \
  -d '{"type":"query","session_id":"test","message":"PCB","content":{"query":{"prompt":[{"type":"text","content":{"text":"PCB"}}]}}}'
```

### 测试前端界面
```bash
# 查看界面HTML
curl http://localhost:5000/ | head -50
```

---

## ❓ 常见问题

### Q1: 为什么我无法打开 http://localhost:5000？

**A**: 因为您在本地电脑上，而服务运行在远程环境。解决方案：
1. 使用演示版：打开 `demo_standalone.html`
2. 本地部署：按照"方式二"操作
3. 端口转发：查看平台是否支持

### Q2: 演示版和完整版有什么区别？

**A**:
- **演示版**：显示模拟数据，不连接API，适合查看界面
- **完整版**：连接真实API，提供实时数据分析

### Q3: 如何获取API密钥？

**A**: 需要注册 Coze 平台账号，获取 API 密钥后配置环境变量。

### Q4: 端口被占用怎么办？

**A**: 使用其他端口，例如：
```bash
python main.py -m http -p 8080
```

---

## 📞 获取帮助

如果遇到问题：
1. 查看日志：`tail -f /app/work/logs/bypass/app.log`
2. 检查服务状态：`curl http://localhost:5000/health`
3. 查看详细文档：`README_WEB_INTERFACE.md`

---

## 🎯 推荐方案

根据您的需求选择：

| 需求 | 推荐方案 | 难度 |
|------|---------|------|
| 只想看看界面 | 方式一：演示版 | ⭐ 简单 |
| 需要完整功能 | 方式二：本地部署 | ⭐⭐⭐ 中等 |
| 云平台用户 | 方式三：端口转发 | ⭐⭐ 需要平台支持 |

---

**🎉 选择适合您的方式，开始使用 2026 产业避险参谋长！**
