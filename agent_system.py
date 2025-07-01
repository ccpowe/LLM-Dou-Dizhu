"""
基于LangGraph的斗地主多智能体系统
实现三个AI智能体的循环交互和游戏状态管理
"""

from typing import List, Dict, Any, Optional, Literal, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import logging
import os

from game_logic import Game, Card, parse_cards_from_string
from prompts import (
    format_landlord_prompt, 
    format_farmer_prompt,
    format_bidding_prompt,
    parse_ai_response,
    get_game_history_summary
)

load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """
    LangGraph状态定义
    遵循最佳实践：使用TypedDict和Annotated进行类型化状态管理
    """
    # 游戏核心状态
    game: Game
    current_player_id: str
    
    # LangGraph消息管理
    messages: Annotated[List[BaseMessage], add_messages]
    
    # 游戏流程控制
    game_phase: Literal["bidding", "playing", "finished"]
    bidding_results: Dict[str, bool]  # 叫地主结果
    
    # 玩家决策状态
    player_decision: Dict[str, Any]  # AI决策结果
    move_result: Dict[str, Any]      # 移动执行结果
    
    # 错误处理和重试
    invalid_move_feedback: Optional[str]
    retry_count: int
    
    # 游戏结果
    game_over: bool
    winner: Optional[str]


class LLMAgentManager:
    """LLM智能体管理器"""
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        # 为每个玩家创建独立的LLM实例
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("MODEL_BASE_URL")
        # model_name = os.getenv("MODEL_NAME") or "gpt-4o-mini"
        
        self.llm_instances = {
            "player_1": ChatOpenAI(model=os.getenv("MODEL_NAME_1") or "gpt-4o-mini", api_key=api_key, base_url=base_url),
            "player_2": ChatOpenAI(model=os.getenv("MODEL_NAME_2") or "gpt-4o-mini", api_key=api_key, base_url=base_url),
            "player_3": ChatOpenAI(model=os.getenv("MODEL_NAME_3") or "gpt-4o-mini", api_key=api_key, base_url=base_url)
        }
    
    async def get_player_decision(self, player_id: str, prompt: str) -> str:
        """获取指定玩家的决策"""
        llm = self.llm_instances[player_id]
        
        try:
            # 使用SystemMessage设置角色，HumanMessage提供具体prompt
            messages = [
                SystemMessage(content="你是一个专业的斗地主玩家，请根据游戏状态做出最优决策。"),
                HumanMessage(content=prompt)
            ]
            
            response = await llm.ainvoke(messages)
            content = response.content
            return str(content) if content else ""
            
        except Exception as e:
            logger.error(f"LLM调用失败 - 玩家{player_id}: {e}")
            return "pass"  # 默认过牌


class DoudizhuAgentSystem:
    """斗地主智能体系统主类"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.agent_manager = LLMAgentManager(model_name)
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """
        构建LangGraph工作流
        遵循最佳实践：清晰的节点职责分离和条件边设计
        """
        # 创建状态图
        workflow = StateGraph(GraphState)
        
        # 添加节点
        workflow.add_node("start_game", self._start_game_node)
        workflow.add_node("bidding_phase", self._bidding_phase_node)
        workflow.add_node("determine_landlord", self._determine_landlord_node)
        workflow.add_node("get_player_decision", self._player_decision_node)
        workflow.add_node("process_move", self._process_move_node)
        workflow.add_node("fallback_strategy", self._fallback_strategy_node)  # 新增兜底策略节点
        
        # 设置入口点
        workflow.add_edge(START, "start_game")
        
        # 添加边
        workflow.add_edge("start_game", "bidding_phase")
        workflow.add_edge("bidding_phase", "determine_landlord")
        
        # 条件边：从determine_landlord到游戏主循环
        workflow.add_conditional_edges(
            "determine_landlord",
            self._route_after_landlord_selection,
            {
                "start_playing": "get_player_decision",
                "no_landlord": END  # 如果没人叫地主，游戏结束
            }
        )
        
        # 去掉直接边，使用条件边控制流程
        workflow.add_conditional_edges(
            "get_player_decision",
            lambda state: "process_move",  # 总是流向process_move
            {
                "process_move": "process_move"
            }
        )
        
        # 关键条件边：游戏主循环路由
        workflow.add_conditional_edges(
            "process_move",
            self._route_game_flow,
            {
                "continue_game": "get_player_decision",
                "retry_move": "get_player_decision", 
                "fallback_strategy": "fallback_strategy",  # 新增兜底策略路由
                "game_over": END
            }
        )
        
        # 兜底策略节点的路由
        workflow.add_conditional_edges(
            "fallback_strategy",
            self._route_after_fallback,
            {
                "continue_game": "get_player_decision",
                "game_over": END
            }
        )
        
        # 编译工作流
        return workflow.compile()
    
    # ========== 节点函数 ==========
    
    def _start_game_node(self, state: GraphState) -> Dict[str, Any]:
        """游戏初始化节点"""
        logger.info("初始化斗地主游戏")
        
        # 创建新游戏实例
        game = Game()
        game.deal_cards()
        
        return {
            "game": game,
            "current_player_id": "player_1",
            "game_phase": "bidding",
            "bidding_results": {},
            "invalid_move_feedback": None,
            "retry_count": 0,
            "game_over": False,
            "winner": None,
            "messages": [SystemMessage(content="斗地主游戏开始，进入叫地主阶段")]
        }
    
    async def _bidding_phase_node(self, state: GraphState) -> Dict[str, Any]:
        """叫地主阶段节点"""
        logger.info("开始叫地主阶段")
        
        game = state["game"]
        bidding_results = {}
        messages = []
        
        players = ["player_1", "player_2", "player_3"]
        current_bid = 0
        landlord_candidate = None
        
        # 循环叫地主，直到所有玩家都叫过或有人叫了3分
        for _ in range(len(players) * 2):  # 最多两轮叫地主
            for player_id in players:
                if landlord_candidate and current_bid == 3:
                    break # 已经有人叫了3分，叫地主结束
                
                # 构建叫地主prompt
                prompt = format_bidding_prompt(
                    player_cards=game.get_hand_summary(player_id),
                    current_bid=current_bid,
                    player_id=player_id
                )
                
                # 调用AI获取决策
                ai_response = await self.agent_manager.get_player_decision(player_id, prompt)
                decision = parse_ai_response(ai_response)
                
                action = decision.get("action")
                bid_score = decision.get("score", 0)
                
                logger.info(f"{player_id} 叫地主决策: {action}, 分数: {bid_score}")
                
                if action == "bid" and bid_score > current_bid:
                    current_bid = bid_score
                    landlord_candidate = player_id
                    messages.append(SystemMessage(content=f"{player_id} 叫了 {bid_score} 分"))
                    bidding_results[player_id] = True
                else:
                    messages.append(SystemMessage(content=f"{player_id} 不叫"))
                    bidding_results[player_id] = False
            
            if landlord_candidate and current_bid == 3:
                break # 已经有人叫了3分，叫地主结束
        
        if landlord_candidate:
            messages.append(SystemMessage(content=f"叫地主阶段完成，{landlord_candidate} 成为地主"))
        else:
            messages.append(SystemMessage(content="叫地主阶段完成，没有玩家叫地主"))
        
        return {
            "bidding_results": bidding_results,
            "messages": messages
        }
    
    def _determine_landlord_node(self, state: GraphState) -> Dict[str, Any]:
        """确定地主节点"""
        bidding_results = state["bidding_results"]
        game = state["game"]
        
        # 找到叫地主的玩家
        landlord = None
        for player, called in bidding_results.items():
            if called:
                landlord = player
                break
        
        if landlord:
            game.set_landlord(landlord)
            logger.info(f"{landlord} 成为地主")
            
            return {
                "game": game,
                "current_player_id": landlord,
                "game_phase": "playing",
                "messages": [SystemMessage(content=f"{landlord}成为地主，游戏开始")]
            }
        else:
            logger.info("没有玩家叫地主")
            return {
                "game_over": True,
                "messages": [SystemMessage(content="没有玩家叫地主，游戏结束")]
            }
    
    async def _player_decision_node(self, state: GraphState) -> Dict[str, Any]:
        """玩家决策节点 - 核心AI交互"""
        current_player = state["current_player_id"]
        game = state["game"]
        
        logger.info(f"轮到 {current_player} 行动")
        
        # 构建prompt
        prompt = self._build_player_prompt(game, current_player, state.get("invalid_move_feedback"))
        
        # 调用AI获取决策
        try:
            ai_response = await self.agent_manager.get_player_decision(current_player, prompt)
            decision = parse_ai_response(ai_response)
            
            logger.info(f"{current_player} AI决策: {decision}")
            
            # 确保状态更新是独立的，避免引用问题
            result = {
                "messages": [
                    HumanMessage(content=prompt),
                    AIMessage(content=ai_response, name=current_player)
                ],
                "player_decision": decision.copy(),  # 深拷贝决策
                "invalid_move_feedback": None,
                "retry_count": state.get("retry_count", 0)  # 保持重试计数
            }
            
            logger.info(f"决策节点返回: player_decision = {result['player_decision']}")
            return result
            
        except Exception as e:
            logger.error(f"AI决策失败: {e}")
            return {
                "player_decision": {"action": "pass"},
                "messages": [SystemMessage(content=f"{current_player}决策失败，自动过牌")],
                "retry_count": state.get("retry_count", 0)
            }
    
    def _process_move_node(self, state: GraphState) -> Dict[str, Any]:
        """处理玩家动作节点"""
        current_player = state["current_player_id"]
        # 直接从状态中获取player_decision，不提供默认值
        decision = state["player_decision"]
        game = state["game"]
        
        logger.info(f"=== 处理 {current_player} 的动作 ===")
        logger.info(f"完整状态键: {list(state.keys())}")
        logger.info(f"接收到的决策: {decision}")
        logger.info(f"决策类型: {type(decision)}")
        logger.info(f"处理前当前玩家: {game.state.current_player}")
        
        # 验证决策有效性
        if not decision or not isinstance(decision, dict) or "action" not in decision:
            logger.error(f"无效的决策对象: {decision}")
            return {
                "invalid_move_feedback": "决策对象无效",
                "retry_count": state.get("retry_count", 0) + 1,
                "move_result": {"success": False, "message": "决策无效"}
            }
        
        if decision["action"] == "pass":
            # 处理过牌
            success, message = game.pass_turn(current_player)
            next_player = game.state.current_player
            
            logger.info(f"过牌处理: {current_player} -> {next_player}, 成功: {success}")
            
            # 检查游戏是否结束
            result = {
                "game": game,
                "current_player_id": next_player,  # 明确更新当前玩家
                "move_result": {"success": success, "message": message},
                "messages": [SystemMessage(content=f"{current_player}: {message}")],
                "retry_count": 0  # 重置重试计数
            }
            
            # 如果游戏结束，添加相应状态
            if game.state.game_over:
                result["game_over"] = True
                result["winner"] = game.state.winner
                logger.info(f"游戏结束！获胜方: {game.state.winner}")
            
            return result
        
        elif decision["action"] == "play":
            # 处理出牌
            cards_str = decision.get("cards", "")
            logger.info(f"尝试出牌: {cards_str}")
            
            cards = self._parse_cards_string(cards_str, game, current_player)
            
            if not cards:
                logger.warning(f"牌型解析失败: {cards_str}")
                return {
                    "invalid_move_feedback": f"无法解析牌型: {cards_str}",
                    "retry_count": state.get("retry_count", 0) + 1,
                    "move_result": {"success": False, "message": "牌型解析失败"}
                }
            
            success, message = game.play_cards(current_player, cards)
            
            if success:
                next_player = game.state.current_player
                logger.info(f"出牌成功: {current_player} -> {next_player}, 牌型: {cards_str}")
                
                result = {
                    "game": game,
                    "current_player_id": next_player,  # 明确更新当前玩家
                    "move_result": {"success": True, "message": message},
                    "messages": [SystemMessage(content=f"{current_player}: {message}")],
                    "retry_count": 0  # 重置重试计数
                }
                
                # 检查游戏是否结束
                if game.state.game_over:
                    result["game_over"] = True
                    result["winner"] = game.state.winner
                    logger.info(f"游戏结束！获胜方: {game.state.winner}")
                
                return result
            else:
                logger.warning(f"出牌失败: {current_player}, {message}")
                return {
                    "invalid_move_feedback": message,
                    "retry_count": state.get("retry_count", 0) + 1,
                    "move_result": {"success": False, "message": message}
                }
        
        else:
            logger.error(f"未知的动作类型: {decision}")
            return {
                "invalid_move_feedback": "未知的动作类型",
                "retry_count": state.get("retry_count", 0) + 1,
                "move_result": {"success": False, "message": "未知动作"}
            }
    
    def _fallback_strategy_node(self, state: GraphState) -> Dict[str, Any]:
        """兜底策略节点：当重试次数过多时尝试智能兜底"""
        current_player = state["current_player_id"]
        game = state["game"]
        
        logger.warning(f"执行兜底策略：为 {current_player}")
        
        try:
            # 首先尝试过牌
            success, message = game.pass_turn(current_player)
            if success:
                logger.info(f"兜底策略成功：{current_player} 过牌，切换到 {game.state.current_player}")
                return {
                    "game": game,
                    "current_player_id": game.state.current_player,
                    "retry_count": 0,
                    "move_result": {"success": True, "message": f"兜底策略：{message}"},
                    "messages": [SystemMessage(content=f"兜底策略：{current_player} 强制过牌")]
                }
            else:
                # 无法过牌，尝试出最小的单牌
                logger.warning(f"无法过牌：{message}，尝试出最小单牌")
                
                # 获取玩家手牌
                player_hand = game.state.player_hands[current_player]
                if not player_hand.cards:
                    logger.error(f"玩家 {current_player} 没有手牌")
                    return {
                        "game_over": True,
                        "move_result": {"success": False, "message": "兜底策略失败：没有手牌"}
                    }
                
                # 找到最小的单牌
                sorted_cards = sorted(player_hand.cards, key=lambda c: c.rank)
                smallest_card = sorted_cards[0]
                
                logger.info(f"兜底策略：尝试出最小单牌 {smallest_card}")
                
                # 尝试出牌
                success, result_message = game.play_cards(current_player, [smallest_card])
                if success:
                    logger.info(f"兜底策略成功：{current_player} 出牌 {smallest_card}")
                    return {
                        "game": game,
                        "current_player_id": game.state.current_player,
                        "retry_count": 0,
                        "move_result": {"success": True, "message": f"兜底策略：出牌 {smallest_card}"},
                        "messages": [SystemMessage(content=f"兜底策略：{current_player} 出牌 {smallest_card}")]
                    }
                else:
                    logger.error(f"兜底策略失败：无法出牌 {smallest_card} - {result_message}")
                    return {
                        "game_over": True,
                        "move_result": {"success": False, "message": f"兜底策略失败：{result_message}"}
                    }
                    
        except Exception as e:
            logger.error(f"兜底策略异常: {e}")
            return {
                "game_over": True,
                "move_result": {"success": False, "message": f"兜底策略异常：{str(e)}"}
            }
    
    # ========== 条件边函数 ==========
    
    def _route_after_landlord_selection(self, state: GraphState) -> str:
        """地主选择后的路由"""
        if state["game"].state.landlord:
            return "start_playing"
        else:
            return "no_landlord"
    
    def _route_game_flow(self, state: GraphState) -> str:
        """游戏主循环路由逻辑（修复版本）"""
        move_result = state.get("move_result", {})
        retry_count = state.get("retry_count", 0)
        
        # 检查是否游戏结束
        if state["game"].state.game_over:
            logger.info("游戏结束，路由到 game_over")
            return "game_over"
        
        # 检查是否移动失败且需要重试
        if not move_result.get("success", False):
            if retry_count >= 2:
                # 重试次数过多，路由到兜底策略节点
                logger.info(f"重试次数过多 ({retry_count + 1}/3)，路由到兜底策略")
                return "fallback_strategy"
            else:
                logger.info(f"移动失败，重试 {retry_count + 1}/3")
                return "retry_move"
        
        # 成功移动，继续游戏
        logger.info(f"移动成功，当前玩家: {state['current_player_id']}")
        return "continue_game"
    
    def _route_after_fallback(self, state: GraphState) -> str:
        """兜底策略后的路由"""
        if state.get("game_over", False):
            return "game_over"
        else:
            return "continue_game"
    
    # ========== 辅助函数 ==========
    
    def _build_player_prompt(self, game: Game, player_id: str, feedback: Optional[str] = None) -> str:
        """构建玩家prompt"""
        state = game.state
        player_cards = game.get_hand_summary(player_id)
        game_history = get_game_history_summary(state.turn_history, player_id)
        
        # 根据玩家角色选择不同的prompt模板
        if player_id == state.landlord:
            # 地主prompt
            other_players = [p for p in ["player_1", "player_2", "player_3"] if p != player_id]
            return format_landlord_prompt(
                player_cards=player_cards,
                cards_count=state.player_hands[player_id].get_card_count(),
                farmer1_count=state.player_hands[other_players[0]].get_card_count(),
                farmer2_count=state.player_hands[other_players[1]].get_card_count(),
                last_play=str(state.last_play) if state.last_play else "",
                last_player=state.last_player or "",
                game_history=game_history,
                feedback=feedback or ""
            )
        else:
            # 农民prompt
            landlord = state.landlord
            if landlord is None:
                return ""
            landlord_count = state.player_hands[landlord].get_card_count()
            teammate = [p for p in ["player_1", "player_2", "player_3"] 
                       if p != player_id and p != state.landlord][0]
            teammate_count = state.player_hands[teammate].get_card_count()
            
            return format_farmer_prompt(
                player_cards=player_cards,
                cards_count=state.player_hands[player_id].get_card_count(),
                landlord_count=landlord_count,
                teammate_count=teammate_count,
                last_play=str(state.last_play) if state.last_play else "",
                last_player=state.last_player or "",
                game_history=game_history,
                feedback=feedback or ""
            )
    
    def _parse_cards_string(self, cards_str: str, game: Game, player_id: str) -> List[Card]:
        """解析牌的字符串表示"""
        try:
            parsed_cards = parse_cards_from_string(cards_str)
            
            # 验证解析出的牌是否都在玩家手牌中
            player_hand_cards = set(game.state.player_hands[player_id].cards)
            if not all(card in player_hand_cards for card in parsed_cards):
                logger.warning(f"解析出的牌不在玩家手牌中: {cards_str}")
                return []

            logger.info(f"成功解析牌型: {cards_str} -> {[str(card) for card in parsed_cards]}")
            return parsed_cards
            
        except Exception as e:
            logger.error(f"解析牌型失败: {e}")
            return []

    def _update_current_player(self, state: GraphState) -> Dict[str, Any]:
        """更新当前玩家"""
        game = state["game"]
        current_player = game.state.current_player
        
        logger.info(f"明确更新当前玩家: {current_player}")
        
        return {
            "current_player_id": current_player,
            "game": game
        }
    
    # ========== 公共接口 ==========
    
    async def run_game(self, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """运行完整游戏"""
        try:
            # 初始化状态
            if initial_state is None:
                initial_state = {
                    "messages": [],
                    "game_phase": "bidding",
                    "retry_count": 0
                }
            
            # 执行工作流
            final_state = await self.workflow.ainvoke(initial_state)
            
            return {
                "success": True,
                "final_state": final_state,
                "game_result": {
                    "winner": final_state.get("winner"),
                    "game_over": final_state.get("game_over", False)
                }
            }
            
        except Exception as e:
            logger.error(f"游戏执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_game_state(self, state: GraphState) -> Dict[str, Any]:
        """获取当前游戏状态（用于前端展示）"""
        if "game" not in state:
            return {"error": "游戏未初始化"}
        
        return state["game"].state.to_dict()

    async def stream_game(self, initial_state: Optional[Dict[str, Any]] = None):
        """
        以流式方式运行游戏，并逐步产生每一步的状态。
        这是一个异步生成器。
        """
        if initial_state is None:
            initial_state = {
                "messages": [],
                "game_phase": "bidding",
                "retry_count": 0
            }
        
        logger.info("开始流式运行游戏")
        
        # 根据LangGraph官方文档，正确设置递归限制
        from langchain_core.runnables.config import RunnableConfig
        config: RunnableConfig = {"recursion_limit": 500}  # 设置更高的递归限制，足够完成一局游戏
        
        # 使用 astream 代替 ainvoke，并传递config
        async for chunk in self.workflow.astream(initial_state, config):
            logger.info(f"流式输出状态块: {list(chunk.keys())}")
            yield chunk


# ========== 工厂函数 ==========

def create_doudizhu_agent_system(model_name: str = "gpt-3.5-turbo") -> DoudizhuAgentSystem:
    """创建斗地主智能体系统实例"""
    return DoudizhuAgentSystem(model_name)


# ========== 测试和调试工具 ==========

async def run_test_game():
    """运行测试游戏"""
    system = create_doudizhu_agent_system()
    result = await system.run_game()
    
    if result["success"]:
        print("游戏成功完成！")
        print(f"获胜方: {result['game_result']['winner']}")
    else:
        print(f"游戏执行失败: {result['error']}")
    
    return result


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_test_game()) 