import type { GameState } from "@/app/page"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CardComponent } from "@/components/card-component"

interface GameStatusProps {
  gameState: GameState
}

export function GameStatus({ gameState }: GameStatusProps) {
  const getStatusText = () => {
    switch (gameState.game_status) {
      case "bidding":
        return "叫地主阶段"
      case "in_progress":
        return "游戏进行中"
      case "finished":
        return "游戏结束"
      default:
        return "未知状态"
    }
  }

  const getStatusColor = () => {
    switch (gameState.game_status) {
      case "bidding":
        return "bg-yellow-600"
      case "in_progress":
        return "bg-blue-600"
      case "finished":
        return "bg-green-600"
      default:
        return "bg-gray-600"
    }
  }

  return (
    <Card className="bg-gray-800 border-gray-700 p-6 min-w-96">
      <div className="text-center">
        <Badge className={`${getStatusColor()} mb-4`}>{getStatusText()}</Badge>

        {/* Landlord Extra Cards */}
        {gameState.landlord_extra_cards.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm text-gray-400 mb-2">地主底牌</h3>
            <div className="flex justify-center gap-1">
              {gameState.landlord_extra_cards.map((cardCode, index) => (
                <CardComponent key={index} cardCode={cardCode} isFaceUp={gameState.game_status !== "bidding"} />
              ))}
            </div>
          </div>
        )}

        {/* Last Move */}
        {gameState.last_move && (
          <div className="mb-4">
            <h3 className="text-sm text-gray-400 mb-2">上一手牌</h3>
            {gameState.last_move.move_type === "pass" ? (
              <div className="text-gray-500 italic">Pass</div>
            ) : (
              <div className="flex justify-center gap-1">
                {gameState.last_move.cards_played.map((cardCode, index) => (
                  <CardComponent key={index} cardCode={cardCode} isFaceUp={true} />
                ))}
              </div>
            )}
            <div className="text-xs text-gray-500 mt-1">
              by {gameState.players.find((p) => p.id === gameState.last_move?.player_id)?.name}
            </div>
          </div>
        )}

        {/* Current Turn */}
        {gameState.game_status === "in_progress" && (
          <div className="text-sm">
            <span className="text-gray-400">当前回合: </span>
            <span className="text-blue-400 font-semibold">
              {gameState.players.find((p) => p.id === gameState.turn_player_id)?.name}
            </span>
          </div>
        )}
      </div>
    </Card>
  )
}
