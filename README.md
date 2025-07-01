# LLM Dou Dizhu - AI 斗地主多智能体系统

这是一个基于大语言模型（LLM）的全栈AI斗地主游戏项目。后端采用 Python、FastAPI 和 LangGraph 构建多智能体系统，前端则使用 Next.js 和 React 实现交互界面。

## ✨ 项目特点

- 🤖 **多智能体对战**: 三个由 LLM 驱动的智能体（一个地主，两个农民）进行游戏。
- 🌐 **全栈应用**: 包含 FastAPI 后端和 Next.js 前端，提供完整的游戏体验。
- 🚀 **现代技术栈**: 后端使用 `uv`、`FastAPI`、`LangGraph`，前端使用 `Next.js`、`React`、`TypeScript`。
- 🎮 **完整游戏逻辑**: 实现了斗地主的核心规则，包括叫地主、出牌、牌型验证和胜负判断。
- 🔧 **模块化与可扩展**: 代码结构清晰，分为前端和后端，易于独立开发和扩展。
- 📝 **详细日志**: 内置强大的日志系统，方便调试和追踪游戏进程。

## 🛠️ 技术栈

- **后端**:
  - **框架**: FastAPI
  - **Python版本**: 3.11+
  - **包管理器**: uv
  - **AI编排**: LangGraph, LangChain
  - **Web服务器**: Uvicorn
- **前端**:
  - **框架**: Next.js, React
  - **语言**: TypeScript
  - **包管理器**: pnpm
  - **UI**: Tailwind CSS, shadcn/ui

## 🚀 快速开始

### 1. 环境要求

- **Python 3.11+**
- **Node.js** (推荐 v20+) 和 **pnpm**
- **uv** (推荐的 Python 包管理器)
- **OpenAI API Key** (或其他兼容的 LLM 服务)

### 2. 后端设置

首先，进入项目根目录。

**a. 安装依赖**

推荐使用 `uv` 进行虚拟环境管理和依赖安装。

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

**b. 配置环境变量**

复制 `.env.example` 文件为 `.env`，并填入你的配置。

```bash
# .env
# OpenAI配置
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_BASE_URL="https://api.openai.com/v1"

# 服务配置
HOST="0.0.0.0"
PORT=8000
LOG_LEVEL="INFO"
```

**c. 启动后端服务**

```bash
python main.py
```

服务启动后，API 文档位于 `http://localhost:8000/docs`。

### 3. 前端设置

**a. 进入前端目录**

```bash
cd frontend
```

**b. 安装依赖**

```bash
pnpm install
```

**c. 启动前端开发服务器**

```bash
pnpm dev
```

前端应用将运行在 `http://localhost:3000`。

## 📂 项目结构

```
.
├── frontend/         # Next.js 前端应用
│   ├── app/          # 页面和路由
│   ├── components/   # React 组件
│   └── package.json  # 前端依赖
│
├── agent_system.py   # LangGraph 智能体系统
├── game_logic.py     # 斗地主核心游戏逻辑
├── main.py           # FastAPI 应用入口
├── prompts.py        # LLM 的 Prompt 模板
├── requirements.txt  # Python 依赖
├── pyproject.toml    # Python 项目配置 (uv)
└── README.md         # 项目文档
```

## 📖 API 使用指南

### 创建新游戏

```bash
curl -X POST "http://localhost:8000/api/game/start" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "gpt-3.5-turbo"
     }'
```

### 查询游戏状态

```bash
curl "http://localhost:8000/api/game/{game_id}/state"
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request。

## 📄 许可证

MIT License