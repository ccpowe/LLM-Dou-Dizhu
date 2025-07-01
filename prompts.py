"""
斗地主AI智能体的Prompt模板
包含角色设定、游戏规则说明和决策指导
"""

from typing import Dict, Any


# 斗地主基本规则说明
GAME_RULES = """
斗地主游戏规则：
1. 三人游戏，一人做地主，两人做农民
2. 地主获得3张底牌，总共20张牌；农民各17张牌
3. 地主先出牌，其他玩家按顺序出牌
4. 必须压过上家的牌，或者选择过牌
5. 如果连续两人过牌，下一位玩家可以出任意牌型,但不能过牌

牌型说明：
- 单牌：任意一张牌
- 对子：两张相同点数的牌
- 三张：三张相同点数的牌  
- 三带一：三张+一张单牌
- 三带二：三张+一对
- 顺子：连续5张或以上的单牌（A后面不能接2）
- 连对：连续3对或以上的对子
- 飞机：连续的三张，可带同数量的单牌或对子
- 炸弹：四张相同点数的牌，可以压任何非炸弹牌型
- 王炸：大王+小王，最大的牌型

牌力大小：3 < 4 < 5 < 6 < 7 < 8 < 9 < 10 < J < Q < K < A < 2 < 小王 < 大王

牌型比较规则：
1. 王炸最大，可以压任何牌。
2. 炸弹次之，可以压任何非炸弹牌型和比自己小的炸弹。
3. 其他牌型必须同类型且点数更大才能压过。例如，对子只能用更大的对子压，顺子只能用起始点数更大的同长度顺子压。
"""

# 地主角色提示
LANDLORD_PROMPT = """
你是斗地主游戏中的地主玩家。你的目标是尽快出完所有手牌获得胜利。

{game_rules}

当前游戏状态：
- 你的身份：地主
- 你的手牌：{player_cards}
- 剩余牌数：{cards_count}张
- 农民1剩余：{farmer1_count}张
- 农民2剩余：{farmer2_count}张
- 上一手牌：{last_play}（由{last_player}出）
- 游戏历史：{game_history}

策略建议：
1. 优先出小牌，保留大牌和炸弹用于关键时刻
2. 注意农民的剩余牌数，防止他们抢先出完
3. 合理使用炸弹，在农民即将获胜时打出
4. 尽量拆散农民的牌型连接

请根据当前情况选择你的行动：
1. 出牌：指定具体要出的牌（格式：play ♠3 ♥4 ♦5 或 play 🃏 🂿，牌之间用空格分隔）
2. 过牌：如果无法或不想出牌（格式：pass）

{feedback}

重要提示：如果系统反馈你的出牌无效，请仔细阅读反馈信息，并尝试修正你的出牌策略。不要重复无效的牌型。

你的决策：
"""

# 农民角色提示  
FARMER_PROMPT = """
你是斗地主游戏中的农民玩家。你需要与另一位农民合作，阻止地主获胜。

{game_rules}

当前游戏状态：
- 你的身份：农民
- 你的手牌：{player_cards}
- 剩余牌数：{cards_count}张
- 地主剩余：{landlord_count}张
- 队友剩余：{teammate_count}张
- 上一手牌：{last_play}（由{last_player}出）
- 游戏历史：{game_history}

策略建议：
1. 与队友协作，优先让手牌少的农民出完
2. 适时压制地主的牌，不让地主轻松过牌
3. 保护队友，在队友即将获胜时配合出牌
4. 关键时刻可以牺牲自己的牌力帮助队友

请根据当前情况选择你的行动：
1. 出牌：指定具体要出的牌（格式：play ♠3 ♥4 ♦5 或 play 🃏 🂿，牌之间用空格分隔）
2. 过牌：如果无法或不想出牌（格式：pass）

{feedback}

重要提示：如果系统反馈你的出牌无效，请仔细阅读反馈信息，并尝试修正你的出牌策略。不要重复无效的牌型。

你的决策：
"""

# 叫地主阶段提示
LANDLORD_BIDDING_PROMPT = """
玩家 {player_id}，你正在参与斗地主游戏的叫地主环节。

你的手牌：{player_cards}
当前最高叫分：{current_bid}分

如果你成为地主，将获得3张底牌，但需要1打2。
如果你选择不叫地主，将成为农民，与另一位农民合作。

评估因素：
1. 你的牌力强度（大牌、炸弹、连牌等）
2. 叫分策略：
   - 0分：不叫
   - 1分：叫地主，但牌力一般
   - 2分：牌力较好，有信心叫地主
   - 3分：牌力极好，强烈希望叫地主

请选择你的行动：
1. 叫分：bid <分数> (例如: bid 1, bid 2, bid 3)
2. 不叫：pass

你的选择：
"""


def format_landlord_prompt(
    player_cards: str,
    cards_count: int,
    farmer1_count: int,
    farmer2_count: int,
    last_play: str,
    last_player: str,
    game_history: str,
    feedback: str = ""
) -> str:
    """格式化地主AI的提示"""
    feedback_text = f"系统反馈：{feedback}\n" if feedback else ""
    
    return LANDLORD_PROMPT.format(
        game_rules=GAME_RULES,
        player_cards=player_cards,
        cards_count=cards_count,
        farmer1_count=farmer1_count,
        farmer2_count=farmer2_count,
        last_play=last_play or "无（你先出牌）",
        last_player=last_player or "无",
        game_history=game_history or "游戏刚开始",
        feedback=feedback_text
    )


def format_farmer_prompt(
    player_cards: str,
    cards_count: int,
    landlord_count: int,
    teammate_count: int,
    last_play: str,
    last_player: str,
    game_history: str,
    feedback: str = ""
) -> str:
    """格式化农民AI的提示"""
    feedback_text = f"系统反馈：{feedback}\n" if feedback else ""
    
    return FARMER_PROMPT.format(
        game_rules=GAME_RULES,
        player_cards=player_cards,
        cards_count=cards_count,
        landlord_count=landlord_count,
        teammate_count=teammate_count,
        last_play=last_play or "无",
        last_player=last_player or "无",
        game_history=game_history or "游戏刚开始",
        feedback=feedback_text
    )


def format_bidding_prompt(player_cards: str, current_bid: int, player_id: str) -> str:
    """格式化叫地主提示"""
    return LANDLORD_BIDDING_PROMPT.format(
        player_cards=player_cards,
        current_bid=current_bid,
        player_id=player_id
    )


def get_game_history_summary(turn_history: list, current_player: str) -> str:
    """生成游戏历史摘要"""
    if not turn_history:
        return "游戏刚开始"
    
    # 只显示最近的几手牌
    recent_turns = turn_history[-6:] if len(turn_history) > 6 else turn_history
    
    history_lines = []
    for player, play in recent_turns:
        if play is None:
            history_lines.append(f"{player}: 过牌")
        else:
            cards_str = " ".join([str(card) for card in play.cards])
            history_lines.append(f"{player}: {cards_str} ({play.card_type.value})")
    
    return "\n".join(history_lines)


# 输出解析模板
OUTPUT_PATTERNS = {
    "play": r"play\s+(.+)",
    "pass": r"pass",
    "call_landlord": r"call_landlord",
}


def parse_ai_response(response: str) -> Dict[str, Any]:
    """解析AI的回复，提取动作和参数。"""
    import re
    import logging
    
    logger = logging.getLogger(__name__)
    original_response = response
    response_lines = response.strip().split('\n')
    
    logger.info(f"解析AI回复: '{original_response}'")

    # 策略1: 寻找明确的决策行，如 "决策：play ..." 或 "play ..."
    decision_line = ""
    for line in reversed(response_lines):
        cleaned_line = line.strip()
        if cleaned_line.lower().startswith(('play', 'pass', '决策：', 'decision:', 'bid')):
            decision_line = cleaned_line
            break

    if decision_line:
        logger.info(f"找到决策行: '{decision_line}'")
        # 从决策行中移除 "决策：" 或 "Decision:" 前缀
        if decision_line.lower().startswith('决策：'):
            decision_line = decision_line[3:].strip()
        elif decision_line.lower().startswith('decision:'):
            decision_line = decision_line[9:].strip()
        
        # 解析动作
        if decision_line.lower().startswith('play'):
            parts = decision_line.split(maxsplit=1)
            if len(parts) > 1:
                cards_str = parts[1].strip()
                # 清理markdown格式和其他干扰字符
                cards_str = re.sub(r'\*+', '', cards_str)  # 移除markdown粗体标记
                cards_str = re.sub(r'[`_~]', '', cards_str)  # 移除其他markdown标记
                cards_str = cards_str.strip()
                logger.info(f"识别为：出牌 - {cards_str}")
                return {"action": "play", "cards": cards_str}
        
        if decision_line.lower() == 'pass':
            logger.info("识别为：过牌")
            return {"action": "pass"}

        if decision_line.lower().startswith('bid'):
            parts = decision_line.split(maxsplit=1)
            if len(parts) > 1 and parts[1].isdigit():
                score = int(parts[1])
                if 0 <= score <= 3:
                    logger.info(f"识别为：叫分 - {score}")
                    return {"action": "bid", "score": score}
                else:
                    logger.warning(f"叫分超出范围 (0-3): {score}")
            logger.warning(f"无法解析叫分: {decision_line}")
            return {"action": "pass"} # 叫分失败则默认过牌

    # 策略2: 如果没有明确的决策行，则在整个响应中搜索关键字（作为后备）
    logger.info("未找到明确决策行，在整个响应中搜索关键字...")
    if re.search(r"\bpass\b", response, re.IGNORECASE):
        logger.info("在文本中找到 'pass' 关键字，识别为：过牌")
        return {"action": "pass"}

    play_match = re.search(r"play\s+(.+)", response, re.IGNORECASE)
    if play_match:
        cards_str = play_match.group(1).strip()
        # 清理markdown格式和其他干扰字符
        cards_str = re.sub(r'\*+', '', cards_str)  # 移除markdown粗体标记
        cards_str = re.sub(r'[`_~]', '', cards_str)  # 移除其他markdown标记
        cards_str = cards_str.strip()
        logger.info(f"在文本中找到 'play' 关键字，识别为：出牌 - {cards_str}")
        return {"action": "play", "cards": cards_str}

    bid_match = re.search(r"bid\s+(\d+)", response, re.IGNORECASE)
    if bid_match:
        score = int(bid_match.group(1))
        if 0 <= score <= 3:
            logger.info(f"在文本中找到 'bid' 关键字，识别为：叫分 - {score}")
            return {"action": "bid", "score": score}
        else:
            logger.warning(f"在文本中找到叫分但超出范围 (0-3): {score}")

    # 策略3: 如果以上都不匹配，则默认过牌
    logger.warning(f"无法解析AI回复，使用默认过牌策略。原文：'{original_response}'")
    return {"action": "pass"}


# 牌名映射表（用于解析AI输出）
CARD_NAME_MAPPING = {
    # 数字牌
    "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
    # 面牌
    "j": 11, "q": 12, "k": 13, "a": 14, "2": 15,
    # 大小王
    "小王": 16, "大王": 17, "小": 16, "大": 17,
    "🃏": 16, "🂿": 17
}

SUIT_MAPPING = {
    "♠": "SPADES", "♥": "HEARTS", "♦": "DIAMONDS", "♣": "CLUBS",
    "黑桃": "SPADES", "红桃": "HEARTS", "方块": "DIAMONDS", "梅花": "CLUBS"
} 