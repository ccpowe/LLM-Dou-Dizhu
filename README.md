# 斗地主多智能体系统

基于LangGraph和FastAPI的AI斗地主游戏系统，实现三个智能体的循环交互和完整游戏流程。

## 项目特点

- 🤖 **多智能体系统**: 使用LangGraph构建三个AI智能体，模拟真实的斗地主游戏
- 🎯 **遵循最佳实践**: 基于LangGraph官方文档的设计模式，确保代码质量和可维护性
- 🚀 **高性能异步**: FastAPI + 异步处理，支持并发游戏会话
- 🎮 **完整游戏逻辑**: 实现完整的斗地主规则，包括牌型识别、出牌验证等
- 📊 **实时状态管理**: 基于状态图的游戏流程控制，支持实时状态查询
- 🔧 **可扩展架构**: 模块化设计，易于扩展新功能和接入不同的LLM

## 系统架构

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   前端界面      │ ◄──────────────► │   FastAPI后端   │
│  (React/Vue)    │                 │                 │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  LangGraph      │
                                    │  智能体系统     │
                                    └─────────────────┘
                                            │
                        ┌───────────────────┼───────────────────┐
                        ▼                   ▼                   ▼
                ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
                │   地主AI     │    │   农民AI 1   │    │   农民AI 2   │
                │  (LLM Agent) │    │  (LLM Agent) │    │  (LLM Agent) │
                └──────────────┘    └──────────────┘    └──────────────┘
```

## 快速开始

### 环境要求

- Python 3.9+
- OpenAI API Key（或其他兼容的LLM提供商）

### 安装依赖

```bash
# 克隆项目
cd agent_framework/game_agent

# 安装依赖
pip install -r requirements.txt

# 或使用uv（推荐）
uv sync
```

### 配置环境变量

创建 `.env` 文件：

```bash
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，使用其他API提供商时修改

# 服务配置
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### 启动服务

```bash
# 启动开发服务器
python main.py

# 或使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health

## API使用指南

### 创建新游戏

```bash
curl -X POST "http://localhost:8000/api/game/start" \
     -H "Content-Type: application/json" \
     -d '{
       "model_name": "gpt-3.5-turbo",
       "player_names": {
         "player_1": "AI地主",
         "player_2": "AI农民1",
         "player_3": "AI农民2"
       }
     }'
```

响应示例：
```json
{
  "game_id": "abc123-def456-ghi789",
  "status": "starting",
  "game_state": {},
  "created_at": "2024-01-01T10:00:00",
  "last_updated": "2024-01-01T10:00:00"
}
```

### 查询游戏状态

```bash
curl "http://localhost:8000/api/game/{game_id}/state"
```

### 游戏控制

```bash
# 暂停游戏
curl -X POST "http://localhost:8000/api/game/{game_id}/action" \
     -H "Content-Type: application/json" \
     -d '{"action": "pause"}'

# 重置游戏
curl -X POST "http://localhost:8000/api/game/{game_id}/action" \
     -H "Content-Type: application/json" \
     -d '{"action": "reset"}'
```

## 核心模块说明

### 1. 游戏逻辑模块 (`game_logic.py`)

实现完整的斗地主规则：
- 扑克牌表示和管理
- 牌型识别和验证
- 游戏状态管理
- 出牌规则检查

```python
from game_logic import Game, Card, Suit

# 创建游戏实例
game = Game()
game.deal_cards()
game.set_landlord("player_1")

# 验证出牌
cards = [Card(Suit.SPADES, 3)]
valid, message, play = game.validate_play("player_1", cards)
```

### 2. 智能体系统 (`agent_system.py`)

基于LangGraph的多智能体协调：
- 状态图定义和管理
- 智能体决策节点
- 条件边和流程控制
- 错误处理和重试机制

```python
from agent_system import create_doudizhu_agent_system

# 创建智能体系统
system = create_doudizhu_agent_system("gpt-3.5-turbo")

# 运行游戏
result = await system.run_game()
```

### 3. Prompt工程 (`prompts.py`)

精心设计的AI提示词：
- 角色设定（地主/农民）
- 游戏状态描述
- 策略指导
- 输出格式规范

### 4. 工具函数 (`utils.py`)

辅助功能模块：
- 牌型解析和转换
- 游戏状态格式化
- 日志配置
- 调试工具

## LangGraph设计模式

本项目严格遵循LangGraph最佳实践：

### 1. 状态管理

```python
class GraphState(TypedDict):
    game: Game
    current_player_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    game_phase: Literal["bidding", "playing", "finished"]
    # ... 其他状态字段
```

### 2. 节点设计

每个节点职责单一，易于测试和维护：

```python
def _player_decision_node(self, state: GraphState) -> Dict[str, Any]:
    """玩家决策节点 - 核心AI交互"""
    # 1. 构建prompt
    # 2. 调用LLM
    # 3. 解析响应
    # 4. 返回状态更新
```

### 3. 条件边

使用条件边实现复杂的游戏流程控制：

```python
def _route_game_flow(self, state: GraphState) -> str:
    """游戏主循环路由逻辑"""
    if state["game"].state.game_over:
        return "game_over"
    elif not move_success and retry_count < 3:
        return "retry_move"
    else:
        return "continue_game"
```

## 性能优化

- **异步处理**: 所有LLM调用都是异步的，支持并发游戏
- **状态缓存**: 游戏状态在内存中缓存，减少计算开销
- **连接池**: 复用HTTP连接，提高API调用效率
- **错误恢复**: 智能重试机制，提高系统稳定性

## 扩展指南

### 添加新的LLM提供商

```python
# 在LLMAgentManager中添加新的模型
class LLMAgentManager:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        if model_name.startswith("claude"):
            from langchain_anthropic import ChatAnthropic
            self.llm_instances = {
                "player_1": ChatAnthropic(model=model_name),
                # ...
            }
```

### 自定义游戏规则

```python
# 继承Game类，重写规则方法
class CustomGame(Game):
    def validate_play(self, player: str, cards: List[Card]) -> Tuple[bool, str, Optional[CardPlay]]:
        # 实现自定义规则
        pass
```

### 添加新的智能体策略

```python
# 在prompts.py中添加新的prompt模板
AGGRESSIVE_PROMPT = """
你是一个激进型斗地主玩家...
"""
```

## 调试和测试

### 启用调试模式

```python
# 在main.py中
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 运行单元测试

```bash
pytest tests/ -v
```

### 手动测试游戏逻辑

```python
# 直接测试智能体系统
from agent_system import run_test_game
import asyncio

result = asyncio.run(run_test_game())
print(f"游戏结果: {result}")
```

## 常见问题

### Q: 如何更换不同的LLM模型？

A: 在创建游戏时指定model_name参数：
```json
{
  "model_name": "gpt-4",  // 或 "claude-3-sonnet", "llama-2-70b" 等
  "player_names": {...}
}
```

### Q: 游戏卡住了怎么办？

A: 检查以下几点：
1. LLM API是否正常响应
2. 游戏状态是否正确
3. 使用调试接口查看详细状态：`GET /api/debug/game/{game_id}`

### Q: 如何提高AI的游戏水平？

A: 可以通过以下方式优化：
1. 改进prompt工程，提供更详细的策略指导
2. 增加游戏历史分析功能
3. 使用更强大的LLM模型
4. 实现强化学习训练

## 贡献指南

欢迎提交Issue和Pull Request！请确保：

1. 代码符合项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档
4. 遵循LangGraph最佳实践

## 许可证

MIT License

## 相关链接

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [项目设计文档](./PLAN.md)
- [智能体系统设计](./AGENT_SYSTEM_DESIGN.md) 