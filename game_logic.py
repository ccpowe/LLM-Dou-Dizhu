"""
斗地主游戏核心逻辑模块
包含扑克牌、手牌管理和游戏规则验证
"""

from typing import List, Dict, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import random


class Suit(Enum):
    """花色枚举"""
    SPADES = "♠"    # 黑桃
    HEARTS = "♥"    # 红桃
    DIAMONDS = "♦"  # 方块
    CLUBS = "♣"     # 梅花


class CardType(Enum):
    """牌型枚举"""
    SINGLE = "single"           # 单牌
    PAIR = "pair"              # 对子
    TRIPLE = "triple"          # 三带
    TRIPLE_SINGLE = "triple_single"    # 三带一
    TRIPLE_PAIR = "triple_pair"        # 三带二
    STRAIGHT = "straight"              # 顺子
    PAIR_STRAIGHT = "pair_straight"    # 连对
    TRIPLE_STRAIGHT = "triple_straight" # 飞机不带
    AIRPLANE_SINGLE = "airplane_single" # 飞机带单牌
    AIRPLANE_PAIR = "airplane_pair"     # 飞机带对子
    BOMB = "bomb"                      # 炸弹
    ROCKET = "rocket"                  # 火箭（王炸）
    INVALID = "invalid"                # 无效牌型


@dataclass
class Card:
    """扑克牌类"""
    suit: Suit
    rank: int  # 3-17，其中14=A, 15=2, 16=小王, 17=大王
    
    def __str__(self) -> str:
        if self.rank == 16:
            return "🃏"  # 小王
        elif self.rank == 17:
            return "🂿"  # 大王
        else:
            rank_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A', 15: '2'}
            rank_str = rank_map.get(self.rank, str(self.rank))
            return f"{self.suit.value}{rank_str}"
    
    def __eq__(self, other) -> bool:
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        return hash((self.suit, self.rank))


@dataclass
class CardPlay:
    """出牌动作"""
    cards: List[Card]
    card_type: CardType
    power: int  # 牌力大小，用于比较
    
    def __str__(self) -> str:
        return f"{[str(card) for card in self.cards]} ({self.card_type.value})"


class Hand:
    """手牌管理类"""
    
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda x: x.rank)
    
    def remove_cards(self, cards: List[Card]) -> bool:
        """移除指定的牌"""
        for card in cards:
            if card in self.cards:
                self.cards.remove(card)
            else:
                return False
        return True
    
    def get_card_count(self) -> int:
        """获取手牌数量"""
        return len(self.cards)
    
    def is_empty(self) -> bool:
        """检查手牌是否为空"""
        return len(self.cards) == 0
    
    def __str__(self) -> str:
        return f"Hand({[str(card) for card in self.cards]})"


class GameState:
    """游戏状态类"""
    
    def __init__(self):
        self.deck: List[Card] = []
        self.player_hands: Dict[str, Hand] = {}
        self.landlord_cards: List[Card] = []  # 地主牌（底牌）
        self.landlord: Optional[str] = None
        self.current_player: str = "player_1"
        self.last_play: Optional[CardPlay] = None
        self.last_player: Optional[str] = None
        self.turn_history: List[Tuple[str, Optional[CardPlay]]] = []
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.pass_count: int = 0  # 连续过牌次数
        
    def to_dict(self) -> Dict:
        """转换为字典格式，用于前端展示"""
        return {
            "player_hands": {
                player: {
                    "cards": [str(card) for card in hand.cards],
                    "count": hand.get_card_count()
                }
                for player, hand in self.player_hands.items()
            },
            "landlord": self.landlord,
            "current_player": self.current_player,
            "last_play": {
                "player": self.last_player,
                "cards": [str(card) for card in self.last_play.cards] if self.last_play else None,
                "card_type": self.last_play.card_type.value if self.last_play else None
            } if self.last_play else None,
            "game_over": self.game_over,
            "winner": self.winner,
            "turn_history": [
                {
                    "player": player,
                    "play": {
                        "cards": [str(card) for card in play.cards] if play else None,
                        "card_type": play.card_type.value if play else None
                    } if play else "pass"
                }
                for player, play in self.turn_history
            ],
            "landlord_extra_cards": [str(card) for card in self.landlord_cards]
        }


class CardAnalyzer:
    """牌型分析器"""
    
    @staticmethod
    def analyze_cards(cards: List[Card]) -> Tuple[CardPlay, str]:
        """分析牌型"""
        if not cards:
            return CardPlay([], CardType.INVALID, 0), "出牌不能为空"
        
        # 按点数分组
        rank_counts = {}
        for card in cards:
            rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
        
        sorted_ranks = sorted(rank_counts.keys())
        counts = list(rank_counts.values())
        counts.sort()
        
        # 王炸
        if len(cards) == 2 and 16 in rank_counts and 17 in rank_counts:
            return CardPlay(cards, CardType.ROCKET, 1000), "合法出牌"
        
        # 炸弹
        if len(cards) == 4 and counts == [4]:
            return CardPlay(cards, CardType.BOMB, 100 + sorted_ranks[0]), "合法出牌"
        
        # 单牌
        if len(cards) == 1:
            return CardPlay(cards, CardType.SINGLE, sorted_ranks[0]), "合法出牌"
        
        # 对子
        if len(cards) == 2 and counts == [2]:
            return CardPlay(cards, CardType.PAIR, sorted_ranks[0]), "合法出牌"
        
        # 三张
        if len(cards) == 3 and counts == [3]:
            return CardPlay(cards, CardType.TRIPLE, sorted_ranks[0]), "合法出牌"
        
        # 三带一
        if len(cards) == 4 and counts == [1, 3]:
            triple_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x])
            return CardPlay(cards, CardType.TRIPLE_SINGLE, triple_rank), "合法出牌"
        
        # 三带一对
        if len(cards) == 5 and counts == [2, 3]:
            triple_rank = max(rank_counts.keys(), key=lambda x: rank_counts[x])
            return CardPlay(cards, CardType.TRIPLE_PAIR, triple_rank), "合法出牌"
        
        # 顺子（至少5张）
        if len(cards) >= 5 and len(set(counts)) == 1 and counts[0] == 1:
            if CardAnalyzer._is_consecutive(sorted_ranks) and max(sorted_ranks) <= 14:
                return CardPlay(cards, CardType.STRAIGHT, min(sorted_ranks)), "合法出牌"
            else:
                return CardPlay(cards, CardType.INVALID, 0), "顺子不连续或包含2/大小王"
        elif len(set(counts)) == 1 and counts[0] == 1 and CardAnalyzer._is_consecutive(sorted_ranks) and max(sorted_ranks) <= 14:
            return CardPlay(cards, CardType.INVALID, 0), "顺子至少需要5张牌"
        
        # 连对（至少3对）
        if len(cards) >= 6 and len(cards) % 2 == 0 and len(set(counts)) == 1 and counts[0] == 2:
            if CardAnalyzer._is_consecutive(sorted_ranks) and max(sorted_ranks) <= 14:
                return CardPlay(cards, CardType.PAIR_STRAIGHT, min(sorted_ranks)), "合法出牌"
            else:
                return CardPlay(cards, CardType.INVALID, 0), "连对不连续或包含2/大小王"
        elif len(cards) < 6 and len(cards) % 2 == 0 and len(set(counts)) == 1 and counts[0] == 2 and CardAnalyzer._is_consecutive(sorted_ranks) and max(sorted_ranks) <= 14:
            return CardPlay(cards, CardType.INVALID, 0), "连对至少需要3对"
        
        # 飞机不带翅膀（至少2个三张）
        if len(cards) >= 6 and len(cards) % 3 == 0 and len(set(counts)) == 1 and counts[0] == 3:
            if CardAnalyzer._is_consecutive(sorted_ranks) and max(sorted_ranks) <= 14:
                return CardPlay(cards, CardType.TRIPLE_STRAIGHT, min(sorted_ranks)), "合法出牌"
            else:
                return CardPlay(cards, CardType.INVALID, 0), "飞机不带不连续或包含2/大小王"
        elif len(cards) < 6 and len(cards) % 3 == 0 and len(set(counts)) == 1 and counts[0] == 3 and CardAnalyzer._is_consecutive(sorted_ranks) and max(sorted_ranks) <= 14:
            return CardPlay(cards, CardType.INVALID, 0), "飞机不带至少需要2个三张"
        
        # 飞机带单牌
        triple_ranks = [rank for rank, count in rank_counts.items() if count == 3]
        single_ranks = [rank for rank, count in rank_counts.items() if count == 1]
        if len(triple_ranks) >= 2 and len(single_ranks) == len(triple_ranks):
            if CardAnalyzer._is_consecutive(triple_ranks) and max(triple_ranks) <= 14:
                return CardPlay(cards, CardType.AIRPLANE_SINGLE, min(triple_ranks)), "合法出牌"
            else:
                return CardPlay(cards, CardType.INVALID, 0), "飞机带单牌不连续或包含2/大小王"
        elif len(triple_ranks) < 2 and len(single_ranks) == len(triple_ranks):
            return CardPlay(cards, CardType.INVALID, 0), "飞机带单牌至少需要2个三张"
        
        # 飞机带对子
        pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
        if len(triple_ranks) >= 2 and len(pair_ranks) == len(triple_ranks):
            if CardAnalyzer._is_consecutive(triple_ranks) and max(triple_ranks) <= 14:
                return CardPlay(cards, CardType.AIRPLANE_PAIR, min(triple_ranks)), "合法出牌"
            else:
                return CardPlay(cards, CardType.INVALID, 0), "飞机带对子不连续或包含2/大小王"
        elif len(triple_ranks) < 2 and len(pair_ranks) == len(triple_ranks):
            return CardPlay(cards, CardType.INVALID, 0), "飞机带对子至少需要2个三张"
        
        return CardPlay(cards, CardType.INVALID, 0), "无效的牌型"
    
    @staticmethod
    def _is_consecutive(ranks: List[int]) -> bool:
        """检查点数是否连续"""
        if len(ranks) <= 1:
            return True
        for i in range(1, len(ranks)):
            if ranks[i] != ranks[i-1] + 1:
                return False
        return True


class Game:
    """斗地主游戏主类"""
    
    def __init__(self):
        self.state = GameState()
        self._create_deck()
    
    def _create_deck(self):
        """创建完整的牌组"""
        # 普通牌：3-15（3-K=3-13, A=14, 2=15）
        for rank in range(3, 16):
            for suit in Suit:
                self.state.deck.append(Card(suit, rank))
        
        # 大小王
        self.state.deck.append(Card(Suit.SPADES, 16))  # 小王
        self.state.deck.append(Card(Suit.SPADES, 17))  # 大王
    
    def deal_cards(self):
        """发牌"""
        random.shuffle(self.state.deck)
        
        # 底牌（地主牌）
        self.state.landlord_cards = self.state.deck[:3]
        
        # 给三个玩家发牌
        for i, player in enumerate(["player_1", "player_2", "player_3"]):
            cards = self.state.deck[3 + i * 17:3 + (i + 1) * 17]
            self.state.player_hands[player] = Hand(cards)
    
    def set_landlord(self, player: str):
        """设置地主"""
        self.state.landlord = player
        # 地主获得底牌
        self.state.player_hands[player].cards.extend(self.state.landlord_cards)
        self.state.player_hands[player].cards.sort(key=lambda x: x.rank)
        self.state.current_player = player
    
    def validate_play(self, player: str, cards: List[Card]) -> Tuple[bool, str, Optional[CardPlay]]:
        """验证出牌是否合法"""
        if player != self.state.current_player:
            return False, "不是你的回合", None
        
        if self.state.game_over:
            return False, "游戏已结束", None
        
        # 检查玩家是否拥有这些牌
        player_hand = self.state.player_hands[player]
        for card in cards:
            if card not in player_hand.cards:
                return False, f"你没有这张牌：{card}", None
        
        # 分析牌型
        card_play, message = CardAnalyzer.analyze_cards(cards)
        if card_play.card_type == CardType.INVALID:
            return False, message, None
        
        # 检查是否可以压过上家
        if self.state.last_play is not None:
            if not self._can_beat(card_play, self.state.last_play):
                return False, "牌力不足，无法压过上家", None
        
        return True, "合法出牌", card_play
    
    def _can_beat(self, new_play: CardPlay, last_play: CardPlay) -> bool:
        """判断新出的牌是否能压过上家"""
        # 王炸可以压过任何牌
        if new_play.card_type == CardType.ROCKET:
            return True
        
        # 炸弹可以压过非炸弹和比自己小的炸弹
        if new_play.card_type == CardType.BOMB:
            if last_play.card_type != CardType.BOMB and last_play.card_type != CardType.ROCKET:
                return True
            return new_play.power > last_play.power
        
        # 其他牌型必须同类型且更大
        if new_play.card_type == last_play.card_type:
            return new_play.power > last_play.power
        
        return False
    
    def play_cards(self, player: str, cards: List[Card]) -> Tuple[bool, str]:
        """执行出牌"""
        is_valid, message, card_play = self.validate_play(player, cards)
        
        if not is_valid:
            return False, message
        
        # 从手牌中移除这些牌
        self.state.player_hands[player].remove_cards(cards)
        
        # 更新游戏状态
        self.state.last_play = card_play
        self.state.last_player = player
        self.state.turn_history.append((player, card_play))
        self.state.pass_count = 0
        
        # 检查是否获胜
        if self.state.player_hands[player].is_empty():
            self.state.game_over = True
            if player == self.state.landlord:
                self.state.winner = "landlord"
            else:
                self.state.winner = "farmers"
        
        # 切换到下一个玩家
        self._next_player()
        
        return True, f"出牌成功：{card_play}"
    
    def pass_turn(self, player: str) -> Tuple[bool, str]:
        """过牌"""
        if player != self.state.current_player:
            return False, "不是你的回合"
        
        # 核心规则：当轮到你出牌且场上没有牌时（即你是新一轮的出牌者），你不能过牌。
        # self.state.last_play is None 意味着开启一个新回合，当前玩家必须出牌。
        # 这个判断同时覆盖了地主开局不能pass和一轮pass后获得牌权的玩家不能pass两种情况。
        if self.state.last_play is None:
            return False, "轮到你出牌，必须出牌，不能过牌"

        # 记录过牌
        self.state.turn_history.append((player, None))
        self.state.pass_count += 1
        
        # 如果连续两个玩家过牌，则清空上一手牌，下一个玩家可以出任意牌
        if self.state.pass_count >= 2:
            self.state.last_play = None
            self.state.last_player = None
            self.state.pass_count = 0
        
        # 切换到下一个玩家
        self._next_player()
        
        return True, "过牌成功"
    
    def _next_player(self):
        """切换到下一个玩家"""
        players = ["player_1", "player_2", "player_3"]
        current_index = players.index(self.state.current_player)
        self.state.current_player = players[(current_index + 1) % 3]
    
    def get_possible_plays(self, player: str) -> List[List[Card]]:
        """获取玩家所有可能的出牌组合（AI决策辅助）"""
        # 简化版实现，实际项目中可以更复杂
        hand = self.state.player_hands[player]
        possible_plays = []
        
        # 单牌
        for card in hand.cards:
            possible_plays.append([card])
        
        # TODO: 实现更复杂的组合生成逻辑
        # 这里可以添加对子、三带、顺子等的自动检测
        
        return possible_plays
    
    def get_hand_summary(self, player: str) -> str:
        """获取手牌摘要（用于AI prompt）"""
        hand = self.state.player_hands[player]
        cards_str = ", ".join([str(card) for card in hand.cards])
        return f"手牌({hand.get_card_count()}张): {cards_str}"


def parse_cards_from_string(cards_str: str) -> List[Card]:
    """从字符串解析扑克牌（用于LLM输出解析）"""
    import logging
    logger = logging.getLogger(__name__)
    
    cards = []
    card_tokens = cards_str.split()
    
    suit_map = {
        "♠": Suit.SPADES, "黑桃": Suit.SPADES,
        "♥": Suit.HEARTS, "红桃": Suit.HEARTS,
        "♦": Suit.DIAMONDS, "方块": Suit.DIAMONDS,
        "♣": Suit.CLUBS, "梅花": Suit.CLUBS,
        "🃏": Suit.SPADES, # Small Joker (arbitrary suit)
        "🂿": Suit.SPADES  # Big Joker (arbitrary suit)
    }
    
    rank_map = {
        "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "j": 11, "Q": 12, "q": 12, "K": 13, "k": 13, 
        "A": 14, "a": 14, "2": 15,
        "小王": 16, "大王": 17, "BJ": 16, "RJ": 17
    }

    logger.info(f"解析牌型字符串: '{cards_str}' -> tokens: {card_tokens}")

    for token in card_tokens:
        token = token.strip()
        if not token:
            continue

        suit = None
        rank = None

        # Handle Jokers first
        if token == "🃏" or token.lower() == "小王" or token.upper() == "BJ":
            suit = Suit.SPADES # Arbitrary suit for jokers
            rank = 16
        elif token == "🂿" or token.lower() == "大王" or token.upper() == "RJ":
            suit = Suit.SPADES # Arbitrary suit for jokers
            rank = 17
        else:
            # Try to parse suit and rank
            # Prioritize parsing suit first if present at the beginning
            for s_char, s_enum in suit_map.items():
                if token.startswith(s_char):
                    suit = s_enum
                    rank_str = token[len(s_char):]
                    rank = rank_map.get(rank_str)
                    if rank is not None: # Ensure rank is found
                        break
            
            # If suit not found at start, try to parse rank first (e.g., "3♠")
            if suit is None:
                for r_str, r_int in rank_map.items():
                    if token.endswith(r_str):
                        rank = r_int
                        suit_char = token[:-len(r_str)]
                        suit = suit_map.get(suit_char)
                        if suit:
                            break
        
        if suit and rank:
            cards.append(Card(suit, rank))
            logger.info(f"成功解析: {token} -> {suit.value}{rank}")
        else:
            logger.warning(f"无法解析牌字符串: {token}")
            # 继续解析其他牌，不要因为一张牌失败就全部失败
            
    logger.info(f"解析结果: {len(cards)}张牌 - {[str(card) for card in cards]}")
    return cards 