"""
工具函数模块
包含牌型解析、日志配置、调试工具等辅助功能
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from game_logic import Card, Suit
from prompts import CARD_NAME_MAPPING, SUIT_MAPPING


def setup_logging(level: str = "INFO") -> logging.Logger:
    """配置日志系统"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('game_agent.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)


def parse_card_string(card_str: str) -> Optional[Card]:
    """
    解析单张牌的字符串表示
    支持格式: "3♠", "K♥", "小王", "🃏" 等
    """
    card_str = card_str.strip()
    
    # 处理大小王
    if card_str in ["小王", "小", "🃏"]:
        return Card(Suit.SPADES, 16)
    elif card_str in ["大王", "大", "🂿"]:
        return Card(Suit.SPADES, 17)
    
    # 正则表达式匹配普通牌
    # 支持格式: "3♠", "10♥", "K♦", "A♣"
    pattern = r'([23456789]|10|[JQKA])([♠♥♦♣])'
    match = re.match(pattern, card_str)
    
    if match:
        rank_str, suit_str = match.groups()
        
        # 转换点数
        if rank_str.isdigit():
            rank = int(rank_str)
        elif rank_str == "10":
            rank = 10
        else:
            rank_map = {"J": 11, "Q": 12, "K": 13, "A": 14}
            rank = rank_map.get(rank_str)
            if rank is None:
                return None
        
        # 转换花色
        suit_map = {"♠": Suit.SPADES, "♥": Suit.HEARTS, "♦": Suit.DIAMONDS, "♣": Suit.CLUBS}
        suit = suit_map.get(suit_str)
        
        if rank >= 3 and rank <= 15 and suit is not None:
            return Card(suit, rank)
    
    return None


def parse_cards_from_ai_output(cards_str: str) -> List[Card]:
    """
    从AI输出中解析多张牌
    支持多种格式: "3♠ 4♥ 5♦", "K♣,Q♠,J♥", "小王 大王"
    """
    if not cards_str:
        return []
    
    # 清理输入字符串
    cards_str = cards_str.strip()
    
    # 分割牌名（支持空格、逗号、中文分号等分隔符）
    card_tokens = re.split(r'[,，\s;；]+', cards_str)
    
    cards = []
    for token in card_tokens:
        if token.strip():
            card = parse_card_string(token.strip())
            if card:
                cards.append(card)
    
    return cards


def cards_to_string(cards: List[Card]) -> str:
    """将牌列表转换为字符串表示"""
    return " ".join([str(card) for card in cards])


def validate_player_has_cards(cards: List[Card], player_hand: List[Card]) -> bool:
    """验证玩家是否拥有指定的牌"""
    hand_copy = player_hand.copy()
    
    for card in cards:
        if card in hand_copy:
            hand_copy.remove(card)
        else:
            return False
    
    return True


def get_card_rank_name(rank: int) -> str:
    """获取牌面点数的名称"""
    if rank <= 10:
        return str(rank)
    else:
        rank_map = {11: "J", 12: "Q", 13: "K", 14: "A", 15: "2", 16: "小王", 17: "大王"}
        return rank_map.get(rank, str(rank))


def format_game_state_for_display(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """格式化游戏状态用于前端显示"""
    formatted_state = game_state.copy()
    
    # 格式化手牌显示
    if "player_hands" in formatted_state:
        for player, hand_info in formatted_state["player_hands"].items():
            if "cards" in hand_info:
                # 只显示牌的数量，不显示具体牌面（保护隐私信息）
                hand_info["cards_display"] = f"手牌 {hand_info['count']} 张"
    
    return formatted_state


def calculate_hand_strength(cards: List[Card]) -> float:
    """
    计算手牌强度（用于AI决策辅助）
    返回0-1之间的值，1表示最强
    """
    if not cards:
        return 0.0
    
    # 简化的手牌强度评估
    total_strength = 0.0
    
    # 按点数统计
    rank_counts = {}
    for card in cards:
        rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
    
    # 评分因子
    for rank, count in rank_counts.items():
        # 基础分数：高牌得分更高
        base_score = rank / 17.0
        
        # 组合分数：多张相同点数得分更高
        combo_bonus = {1: 1.0, 2: 1.5, 3: 2.0, 4: 3.0}.get(count, 1.0)
        
        total_strength += base_score * combo_bonus
    
    # 归一化到0-1范围
    max_possible_strength = len(cards) * 3.0  # 理论最大值
    return min(total_strength / max_possible_strength, 1.0)


def find_playable_combinations(hand_cards: List[Card], last_play_type: str = None, last_play_power: int = 0) -> List[List[Card]]:
    """
    找出手牌中所有可能的出牌组合
    用于AI决策时的选择生成
    """
    if not hand_cards:
        return []
    
    playable_combinations = []
    
    # 按点数分组
    rank_groups = {}
    for card in hand_cards:
        if card.rank not in rank_groups:
            rank_groups[card.rank] = []
        rank_groups[card.rank].append(card)
    
    # 生成单牌组合
    for rank, cards in rank_groups.items():
        if not last_play_type or last_play_type == "single":
            if not last_play_power or rank > last_play_power:
                playable_combinations.append([cards[0]])
    
    # 生成对子组合
    for rank, cards in rank_groups.items():
        if len(cards) >= 2:
            if not last_play_type or last_play_type == "pair":
                if not last_play_power or rank > last_play_power:
                    playable_combinations.append(cards[:2])
    
    # 生成三张组合
    for rank, cards in rank_groups.items():
        if len(cards) >= 3:
            if not last_play_type or last_play_type == "triple":
                if not last_play_power or rank > last_play_power:
                    playable_combinations.append(cards[:3])
    
    # 生成炸弹组合
    for rank, cards in rank_groups.items():
        if len(cards) == 4:
            # 炸弹可以压过任何非炸弹牌型
            if not last_play_type or last_play_type != "bomb" or rank > last_play_power:
                playable_combinations.append(cards)
    
    # 王炸组合
    jokers = [card for card in hand_cards if card.rank in [16, 17]]
    if len(jokers) == 2:
        playable_combinations.append(jokers)
    
    # TODO: 添加顺子、连对、飞机等复杂牌型的检测
    
    return playable_combinations


def format_ai_prompt_cards(cards: List[Card]) -> str:
    """
    为AI prompt格式化牌面信息
    按花色和点数整理，便于AI理解
    """
    if not cards:
        return "无牌"
    
    # 按花色分组
    suits_groups = {"♠": [], "♥": [], "♦": [], "♣": [], "王": []}
    
    for card in cards:
        if card.rank >= 16:  # 大小王
            suits_groups["王"].append(card)
        else:
            suits_groups[card.suit.value].append(card)
    
    # 每组内按点数排序
    for suit in suits_groups:
        suits_groups[suit].sort(key=lambda x: x.rank)
    
    # 构建输出字符串
    parts = []
    for suit, suit_cards in suits_groups.items():
        if suit_cards:
            cards_str = " ".join([get_card_rank_name(card.rank) for card in suit_cards])
            parts.append(f"{suit}: {cards_str}")
    
    return " | ".join(parts)


def generate_game_summary(game_state: Dict[str, Any]) -> str:
    """生成游戏状态摘要"""
    summary_parts = []
    
    # 基本信息
    if "landlord" in game_state:
        summary_parts.append(f"地主: {game_state['landlord']}")
    
    if "current_player" in game_state:
        summary_parts.append(f"当前玩家: {game_state['current_player']}")
    
    # 手牌信息
    if "player_hands" in game_state:
        for player, hand_info in game_state["player_hands"].items():
            summary_parts.append(f"{player}: {hand_info['count']}张")
    
    # 上一手牌
    if "last_play" in game_state and game_state["last_play"]:
        last_play = game_state["last_play"]
        if last_play["cards"]:
            cards_str = " ".join(last_play["cards"])
            summary_parts.append(f"上家出牌: {cards_str}")
    
    return " | ".join(summary_parts)


def debug_log_game_state(game_state: Dict[str, Any], logger: logging.Logger):
    """调试日志：记录游戏状态"""
    logger.debug("=== 游戏状态 ===")
    logger.debug(f"地主: {game_state.get('landlord', '未确定')}")
    logger.debug(f"当前玩家: {game_state.get('current_player', '未知')}")
    
    if "player_hands" in game_state:
        for player, hand_info in game_state["player_hands"].items():
            logger.debug(f"{player}: {hand_info['count']}张牌")
    
    if "last_play" in game_state and game_state["last_play"]:
        last_play = game_state["last_play"]
        logger.debug(f"上一手: {last_play.get('cards', [])} ({last_play.get('card_type', '未知')})")
    
    logger.debug("================")


# 常用正则表达式
CARD_PATTERN = re.compile(r'([23456789]|10|[JQKA])([♠♥♦♣])|([小大]王?)|([🃏🂿])')
PLAY_ACTION_PATTERN = re.compile(r'play\s+(.+)', re.IGNORECASE)
PASS_ACTION_PATTERN = re.compile(r'pass', re.IGNORECASE)

# 错误处理装饰器
def handle_game_errors(func):
    """游戏错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"游戏操作失败 {func.__name__}: {e}")
            return None
    return wrapper 