# Industry Risk Advisor | 产业避险参谋

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

> **English** | [中文文档](#中文文档)

---

## Overview

**Industry Risk Advisor** is an AI-powered risk analysis tool that provides real-time cost warnings and procurement recommendations for 6 major industries based on geopolitical dynamics.

## 🎯 Target Industries

| Industry | Description | Key Materials |
|----------|-------------|---------------|
| 🏭 **PCB** | Printed Circuit Board | Copper foil, CCL, Palladium |
| 🛥️ **Yacht** | Yacht Manufacturing | Polyester resin, Gel coat, Engines |
| 💊 **Biopharma** | Biopharmaceuticals | API, Isopropanol, Liquid helium |
| 🔋 **Energy Storage** | New Energy Storage | PVDF, Electrolyte, Aluminum foil |
| 🖨️ **Printing** | Printing Consumables | Toner, ABS/HIPS plastic |
| 📦 **E-commerce** | Cross-border E-commerce | Corrugated boxes, Shipping costs |

## ✨ Key Features

### 📊 Real-time Market Intelligence
- Automatic data collection from web searches
- Professional price API integration
- Multi-source data validation

### 💰 Cost Impact Analysis
- Material-specific cost calculations
- Percentage change tracking
- Risk level assessment (Red/Yellow/Green)

### 🎯 Actionable Recommendations
- Feynman-style explanations for business owners
- Specific timeline for actions
- Alternative supplier suggestions

### 📱 WeChat Integration
- Mobile-friendly interface
- One-click sharing
- Offline viewing support

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/industry-risk-advisor.git
cd industry-risk-advisor

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
python src/main.py
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## 📖 Usage

### 1. View Market Dynamics
- Open the homepage to see real-time market news
- Click on any news item to view detailed analysis

### 2. Query Industry Risk
- Select your industry from the dropdown
- Click "Start Analysis" to get a risk report

### 3. Share via WeChat
- Deploy to Vercel (see deployment guide)
- Share the link in WeChat

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, FastAPI, LangChain, LangGraph |
| **AI Model** | Doubao (doubao-seed-1-8-251228) |
| **Data Source** | Web Search SDK, Professional Price APIs |
| **Frontend** | HTML/CSS/JavaScript |
| **Deployment** | Vercel, Docker |

## 📊 Output Format

```
【Risk Traffic Light】🟡 Yellow Warning

【Dynamics】
- Geopolitical situation analysis
- Material price fluctuation tracking

【Detailed Impact】
- Electrolytic copper foil: +5.7% (¥10.35/sheet)
- CCL: +6.2% (¥13.63/sheet)
- Total cost impact: +4.27%

【Actionable Recommendations】
1. Lock in raw material orders within 3 days
2. Negotiate price-lock agreements with suppliers
3. Evaluate alternative domestic suppliers
4. Shorten quotation validity to 24-48 hours
```

## 📁 Project Structure

```
industry-risk-advisor/
├── config/                 # Configuration files
│   └── agent_llm_config.json
├── src/
│   ├── agents/            # Agent implementation
│   │   └── agent.py
│   ├── tools/             # Tool definitions
│   │   ├── industry_risk_search.py
│   │   ├── cost_calculator.py
│   │   ├── market_news.py
│   │   └── price_api.py
│   ├── storage/           # Memory & database
│   └── main.py            # Main entry point
├── assets/                # Static files
│   ├── index.html
│   └── industry_knowledge_base.json
├── wechat_industry_advisor.html  # WeChat version
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM API Configuration
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=https://api.coze.cn

# Price API Keys (Optional)
BRENT_CRUDE_API_KEY=your_key
LME_COPPER_API_KEY=your_key
PALLADIUM_API_KEY=your_key
SCFI_API_KEY=your_key
```

## 📱 WeChat Deployment

See [Vercel部署教程-小白专用版.md](Vercel部署教程-小白专用版.md) for detailed instructions.

### Quick Deployment Steps

1. Rename `wechat_industry_advisor.html` to `index.html`
2. Upload to GitHub repository
3. Import to Vercel
4. Get your deployment URL
5. Share in WeChat

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Fork the repository
# Clone your fork
git clone https://github.com/yourusername/industry-risk-advisor.git

# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# Commit your changes
git commit -m 'Add amazing feature'

# Push to the branch
git push origin feature/amazing-feature

# Open a Pull Request
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Doubao AI for providing the language model
- LangChain and LangGraph for the agent framework
- All contributors and users

## 📞 Contact

For questions or suggestions, please open an issue or contact the maintainers.

---

# 中文文档

## 项目简介

**产业避险参谋**是一个基于 AI 的风险分析工具，针对六大行业提供实时成本预警和采购建议。

## 🎯 适用行业

| 行业 | 描述 | 关键原材料 |
|------|------|-----------|
| 🏭 **PCB** | 印刷电路板 | 电解铜箔、覆铜板、钯金 |
| 🛥️ **游艇** | 游艇制造 | 聚酯树脂、胶衣、发动机 |
| 💊 **生物医药** | 生物医药 | API原料药、异丙醇、液氦 |
| 🔋 **新型储能** | 新型储能 | PVDF、电解液、铝箔 |
| 🖨️ **打印耗材** | 打印耗材 | 碳粉、ABS/HIPS塑料 |
| 📦 **跨境电商** | 跨境电商 | 瓦楞纸箱、运费 |

## ✨ 核心功能

### 📊 实时市场情报
- 自动从网络搜索收集数据
- 集成专业价格 API
- 多数据源验证

### 💰 成本影响分析
- 具体材料的成本计算
- 百分比变化追踪
- 风险等级评估（红黄绿）

### 🎯 可操作建议
- 费曼式解释，老板听得懂
- 明确的行动时间线
- 替代供应商建议

### 📱 微信集成
- 移动端友好界面
- 一键分享
- 支持离线查看

## 🚀 快速开始

### 环境要求
- Python 3.9 或更高版本
- pip 包管理器

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/industry-risk-advisor.git
cd industry-risk-advisor

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的 API keys

# 运行应用
python src/main.py
```

### 访问应用

打开浏览器访问：
```
http://localhost:5000
```

## 📱 微信部署

详细教程请查看 [Vercel部署教程-小白专用版.md](Vercel部署教程-小白专用版.md)

### 快速部署步骤

1. 将 `wechat_industry_advisor.html` 重命名为 `index.html`
2. 上传到 GitHub 仓库
3. 在 Vercel 中导入
4. 获取部署链接
5. 在微信中分享

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| **后端** | Python, FastAPI, LangChain, LangGraph |
| **AI 模型** | 豆包 (doubao-seed-1-8-251228) |
| **数据源** | Web Search SDK, 专业价格 API |
| **前端** | HTML/CSS/JavaScript |
| **部署** | Vercel, Docker |

## 🤝 参与贡献

欢迎贡献代码！请随时提交 Pull Request。

## 📝 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 豆包 AI 提供语言模型支持
- LangChain 和 LangGraph 提供智能体框架
- 所有贡献者和用户

---

**Made with ❤️ for industry professionals**
