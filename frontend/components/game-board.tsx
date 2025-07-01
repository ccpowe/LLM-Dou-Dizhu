import type { GameState } from "@/app/page"
import { PlayerArea } from "@/components/player-area"
import { GameStatus } from "@/components/game-status"
import { ActionLog } from "@/components/action-log"

interface GameBoardProps {
  gameState: GameState
}

export function GameBoard({ gameState }: GameBoardProps) {
  const [player1, player2, player3] = gameState.players

  return (
    <div className="game-container bg-gray-900 text-white">
      <div className="container mx-auto p-4 h-full flex flex-col layout-constrained">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 flex-shrink-0">
          <h1 className="text-2xl font-bold text-blue-400">AI 斗地主观察室</h1>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-400">游戏 ID: {gameState.game_id.slice(-8)}</div>
            <div className={`text-sm px-2 py-1 rounded status-transition ${
              gameState.game_status === "in_progress" ? "bg-green-600 text-white" :
              gameState.game_status === "finished" ? "bg-red-600 text-white" :
              "bg-yellow-600 text-white"
            }`}>
              {gameState.game_status === "in_progress" ? "游戏进行中" :
               gameState.game_status === "finished" ? "游戏结束" : "准备中"}
            </div>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-4 gap-4 layout-constrained">
          {/* Main Game Area */}
          <div className="col-span-3 flex flex-col layout-constrained">
            {/* Top Players - 显示所有扑克牌 */}
            <div className="grid grid-cols-2 gap-4 mb-4 flex-shrink-0">
              <PlayerArea 
                player={player2} 
                position="top-left" 
                showCards={true} 
              />
              <PlayerArea 
                player={player3} 
                position="top-right" 
                showCards={true} 
              />
            </div>

            {/* Center Game Status */}
            <div className="flex-1 flex items-center justify-center mb-4 layout-constrained">
              <GameStatus gameState={gameState} />
            </div>

            {/* Bottom Player - 显示所有扑克牌 */}
            <div className="flex-shrink-0 bottom-player">
              <PlayerArea 
                player={player1} 
                position="bottom" 
                showCards={true} 
              />
            </div>
          </div>

          {/* Action Log Sidebar - 固定高度并添加滚动 */}
          <div className="col-span-1 layout-constrained">
            <ActionLog logEntries={gameState.action_log} />
          </div>
        </div>
      </div>
    </div>
  )
}
