下面是我想移动的文件。


# 2. 复制核心后端文件
cp /d:/Code_vs/agent_framework/game_agent/main.py .
cp /d:/Code_vs/agent_framework/game_agent/agent_system.py .
cp /d:/Code_vs/agent_framework/game_agent/game_logic.py .
cp /d:/Code_vs/agent_framework/game_agent/prompts.py .
cp /d:/Code_vs/agent_framework/game_agent/utils.py .
cp /d:/Code_vs/agent_framework/game_agent/logging_config.py .
cp /d:/Code_vs/agent_framework/game_agent/requirements.txt .
cp /d:/Code_vs/agent_framework/game_agent/__init__.py .
cp /d:/Code_vs/agent_framework/game_agent/README.md .

# 3. 创建前端目录并复制核心前端文件
mkdir -p frontend
cd frontend

# 复制前端核心配置文件
cp /d:/Code_vs/agent_framework/game_agent/my-app/package.json .
cp /d:/Code_vs/agent_framework/game_agent/my-app/package-lock.json .
cp /d:/Code_vs/agent_framework/game_agent/my-app/tsconfig.json .
cp /d:/Code_vs/agent_framework/game_agent/my-app/next.config.ts .
cp /d:/Code_vs/agent_framework/game_agent/my-app/next-env.d.ts .
cp /d:/Code_vs/agent_framework/game_agent/my-app/postcss.config.mjs .
cp /d:/Code_vs/agent_framework/game_agent/my-app/eslint.config.mjs .
cp /d:/Code_vs/agent_framework/game_agent/my-app/components.json .
cp /d:/Code_vs/agent_framework/game_agent/my-app/.gitignore .
cp /d:/Code_vs/agent_framework/game_agent/my-app/README.md .

# 复制前端源代码目录
cp -r /d:/Code_vs/agent_framework/game_agent/my-app/app .
cp -r /d:/Code_vs/agent_framework/game_agent/my-app/components .
cp -r /d:/Code_vs/agent_framework/game_agent/my-app/lib .
cp -r /d:/Code_vs/agent_framework/game_agent/my-app/public .

cd ..

# 4. 创建 .env 示例文件
cat > .env.example << 'EOF'
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 服务配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
EOF

# 5. 创建项目根目录的 .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
logs/

# Node.js
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env.local
frontend/.env.development.local
frontend/.env.test.local
frontend/.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

# 6. 提交到 Git
git add .
git commit -m "Initial commit: 斗地主多智能体系统

- 基于 LangGraph 和 FastAPI 的完整后端
- Next.js + React 前端界面
- 支持三个 AI 智能体循环交互
- 完整的斗地主游戏逻辑实现"

# 7. 推送到远程仓库
git push origin main