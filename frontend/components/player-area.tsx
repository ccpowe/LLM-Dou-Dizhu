import type { Player } from "@/app/page"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { HandDisplay } from "@/components/hand-display"
import { Crown, Users, Eye, EyeOff } from "lucide-react"
import { useState } from "react"

interface PlayerAreaProps {
  player: Player
  position: "top-left" | "top-right" | "bottom"
  showCards: boolean
}

export function PlayerArea({ player, position, showCards }: PlayerAreaProps) {
  const [isCardsVisible, setIsCardsVisible] = useState(true)

  const getRoleIcon = () => {
    if (player.role === "landlord") {
      return <Crown className="h-4 w-4 text-yellow-400" />
    } else if (player.role === "farmer") {
      return <Users className="h-4 w-4 text-green-400" />
    }
    return null
  }

  const getRoleColor = () => {
    if (player.role === "landlord") return "bg-yellow-600"
    if (player.role === "farmer") return "bg-green-600"
    return "bg-gray-600"
  }

  const getPlayerNameColor = () => {
    if (player.name.includes("Gemini")) return "text-blue-400"
    if (player.name.includes("GPT")) return "text-green-400"
    if (player.name.includes("BaiDu")) return "text-purple-400"
    return "text-white"
  }

  // 根据位置调整卡片高度
  const getCardHeight = () => {
    switch (position) {
      case "bottom":
        return "min-h-[160px]" // 进一步减少底部玩家区域高度
      case "top-left":
      case "top-right":
        return "min-h-[120px]" // 进一步减少顶部玩家区域高度
      default:
        return "min-h-[120px]"
    }
  }

  return (
    <Card className={`bg-gray-800 border-gray-700 compact-player-card ${getCardHeight()} ${player.is_turn ? "ring-2 ring-blue-400 shadow-lg shadow-blue-400/20" : ""}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className={`font-semibold ${getPlayerNameColor()}`}>
            {player.name}
            {/* 思考中状态紧跟在名称后面 */}
            {player.is_turn && (
              <span className="ml-2 text-blue-400 text-sm">
                <span className="inline-block w-1 h-1 bg-blue-400 rounded-full mr-1 animate-pulse"></span>
                思考中
              </span>
            )}
          </span>
          {getRoleIcon()}
        </div>
        <div className="flex items-center space-x-2">
          {/* 扑克牌可见性切换按钮 */}
          {showCards && (
            <button
              onClick={() => setIsCardsVisible(!isCardsVisible)}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
              title={isCardsVisible ? "隐藏扑克牌" : "显示扑克牌"}
            >
              {isCardsVisible ? (
                <Eye className="h-4 w-4 text-gray-400" />
              ) : (
                <EyeOff className="h-4 w-4 text-gray-400" />
              )}
            </button>
          )}
          
          {player.role !== "pending" && (
            <Badge className={getRoleColor()}>{player.role === "landlord" ? "地主" : "农民"}</Badge>
          )}
          <Badge variant="outline" className="text-white border-gray-600">
            {player.hand_count} 张
          </Badge>
        </div>
      </div>

      {/* 扑克牌显示区域 */}
      <div className="flex-1 mb-1">
        <HandDisplay 
          cards={showCards && isCardsVisible ? player.hand : []} 
          showCards={showCards && isCardsVisible} 
          cardCount={player.hand_count} 
        />
      </div>

      {/* 玩家状态指示器 - 进一步减少上边距 */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>
          {position === "bottom" ? "主视角" : "观察视角"}
        </span>
        {showCards && (
          <span className="text-green-400">
            ● 扑克牌可见
          </span>
        )}
      </div>
    </Card>
  )
}
