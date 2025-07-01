"use client"

import { useState, useEffect } from "react"
import { GameBoard } from "@/components/game-board"
import { WelcomeView } from "@/components/welcome-view"
import { EndGameModal } from "@/components/end-game-modal"

export interface Card {
  suit: "S" | "H" | "D" | "C" | "BJ" | "RJ"
  rank: "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "J" | "Q" | "K" | "A" | "2" | "BJ" | "RJ"
  display: string
}

export interface Player {
  id: string
  name: string
  role: "farmer" | "landlord" | "pending"
  hand: string[]
  hand_count: number
  is_turn: boolean
}

export interface LastMove {
  player_id: string
  move_type: "play" | "pass"
  cards_played: string[]
}

export interface GameState {
  game_id: string
  game_status: "bidding" | "in_progress" | "finished"
  turn_player_id: string
  last_move: LastMove | null
  players: Player[]
  landlord_extra_cards: string[]
  winner: "landlord" | "farmers" | null
  action_log: string[]
}

// API 配置
const API_BASE_URL = "http://localhost:8000"

export default function Home() {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentGameId, setCurrentGameId] = useState<string | null>(null)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)
  const [lastValidGameState, setLastValidGameState] = useState<GameState | null>(null)

  // 组件卸载时清理轮询
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  // 真实API调用函数
  const startNewGame = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // 调用后端API创建新游戏
      const response = await fetch(`${API_BASE_URL}/api/game/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_name: "gpt-3.5-turbo",
          player_names: {
            "player_1": "Agent 1 (Gemini)",
            "player_2": "Agent 2 (GPT-4o)", 
            "player_3": "Agent 3 (Claude)"
          }
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("游戏创建成功:", data)
      
      setCurrentGameId(data.game_id)
      
      // 开始轮询游戏状态
      startPolling(data.game_id)
      
    } catch (err) {
      console.error("创建游戏失败:", err)
      setError(`创建游戏失败: ${err instanceof Error ? err.message : String(err)}`)
    } finally {
      setIsLoading(false)
    }
  }

  // 停止轮询
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      setPollingInterval(null)
      console.log("停止轮询")
    }
  }

  // 轮询游戏状态
  const startPolling = (gameId: string) => {
    console.log("开始轮询游戏状态:", gameId)
    
    // 先清除之前的轮询
    stopPolling()
    
    const pollGameState = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/game/${gameId}/state`)
        
        if (!response.ok) {
          // 如果是404或游戏不存在，可能是游戏已结束
          if (response.status === 404) {
            console.log("游戏不存在，可能已结束")
            
            // 如果有最后的有效状态且游戏已结束，使用该状态
            if (lastValidGameState && lastValidGameState.game_status === "finished") {
              console.log("使用最后的有效游戏状态")
              setGameState(lastValidGameState)
              stopPolling()
              return
            }
            
            // 否则尝试解析错误响应
            try {
              const errorData = await response.json()
              if (errorData.detail === "游戏不存在") {
                console.log("游戏已结束，停止轮询")
                stopPolling()
                return
              }
            } catch (parseErr) {
              console.log("无法解析错误响应")
            }
          }
          
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log("轮询到的游戏状态:", data)
        
        // 转换后端数据格式为前端格式
        if (data.game_state && Object.keys(data.game_state).length > 0) {
          const convertedState = convertBackendStateToFrontend(data)
          setGameState(convertedState)
          setLastValidGameState(convertedState)
          
          // 如果游戏已结束，停止轮询
          if (convertedState.game_status === "finished") {
            console.log("检测到游戏结束，停止轮询")
            stopPolling()
          }
        }
        
      } catch (err) {
        console.error("轮询游戏状态失败:", err)
        setError(`获取游戏状态失败: ${err instanceof Error ? err.message : String(err)}`)
      }
    }

    // 立即执行一次
    pollGameState()
    
    // 每2秒轮询一次
    const interval = setInterval(pollGameState, 2000)
    setPollingInterval(interval)
    
    // 5分钟后停止轮询（安全措施）
    setTimeout(() => {
      stopPolling()
      console.log("轮询超时，停止轮询")
    }, 300000)
    
    return interval
  }

  // 转换后端状态数据为前端格式
  const convertBackendStateToFrontend = (backendData: any): GameState => {
    const backendState = backendData.game_state
    
    // 默认状态
    let gameState: GameState = {
      game_id: backendData.game_id,
      game_status: backendData.status === "running" ? "in_progress" : 
                   backendData.status === "finished" ? "finished" : "bidding",
      turn_player_id: "player_1",
      last_move: null,
      players: [
        {
          id: "player_1",
          name: "Agent 1 (Gemini)",
          role: "pending",
          hand: [],
          hand_count: 17,
          is_turn: false,
        },
        {
          id: "player_2", 
          name: "Agent 2 (GPT-4o)",
          role: "pending",
          hand: [],
          hand_count: 17,
          is_turn: false,
        },
        {
          id: "player_3",
          name: "Agent 3 (Claude)",
          role: "pending",
          hand: [],
          hand_count: 17,
          is_turn: false,
        },
      ],
      landlord_extra_cards: [],
      winner: null,
      action_log: ["游戏开始，正在发牌..."],
    }

    // 如果有真实游戏数据，进行转换
    if (backendState && backendState.player_hands) {
      const playerHands = backendState.player_hands
      
      // 转换玩家数据
      gameState.players = [
        {
          id: "player_1",
          name: "Agent 1 (Gemini)",
          role: backendState.landlord === "player_1" ? "landlord" : 
                (backendState.landlord ? "farmer" : "pending"),
          hand: playerHands.player_1?.cards || [],
          hand_count: playerHands.player_1?.count || 17,
          is_turn: backendState.current_player === "player_1",
        },
        {
          id: "player_2",
          name: "Agent 2 (GPT-4o)",
          role: backendState.landlord === "player_2" ? "landlord" : 
                (backendState.landlord ? "farmer" : "pending"),
          hand: playerHands.player_2?.cards || [],
          hand_count: playerHands.player_2?.count || 17,
          is_turn: backendState.current_player === "player_2",
        },
        {
          id: "player_3",
          name: "Agent 3 (Claude)",
          role: backendState.landlord === "player_3" ? "landlord" : 
                (backendState.landlord ? "farmer" : "pending"),
          hand: playerHands.player_3?.cards || [],
          hand_count: playerHands.player_3?.count || 17,
          is_turn: backendState.current_player === "player_3",
        },
      ]

      // 设置当前回合玩家
      if (backendState.current_player) {
        const playerMap: { [key: string]: string } = {
          "player_1": "player_1",
          "player_2": "player_2", 
          "player_3": "player_3"
        }
        gameState.turn_player_id = playerMap[backendState.current_player] || "player_1"
      }

      // 设置地主底牌
      if (backendState.landlord_cards) {
        gameState.landlord_extra_cards = backendState.landlord_cards
      }

      // 设置上一手牌
      if (backendState.last_play && backendState.last_play.cards) {
        const playerMap: { [key: string]: string } = {
          "player_1": "player_1",
          "player_2": "player_2",
          "player_3": "player_3"
        }
        
        gameState.last_move = {
          player_id: playerMap[backendState.last_play.player] || "player_1",
          move_type: backendState.last_play.cards ? "play" : "pass",
          cards_played: backendState.last_play.cards || []
        }
      }

      // 设置游戏状态
      if (backendState.game_over || backendState.winner) {
        gameState.game_status = "finished"
        if (backendState.winner === "landlord") {
          gameState.winner = "landlord"
        } else if (backendState.winner === "farmers") {
          gameState.winner = "farmers"
        }
      } else if (backendState.landlord) {
        gameState.game_status = "in_progress"
      }
      
      // 额外检查：如果有获胜者，确保游戏状态为结束
      if (backendState.winner && gameState.game_status !== "finished") {
        gameState.game_status = "finished"
      }

      // 构建行动日志
      let actionLog = ["游戏开始，正在发牌..."]
      
      if (backendState.landlord) {
        const landlordName = gameState.players.find(p => p.role === "landlord")?.name || "未知玩家"
        actionLog.push("发牌完成，开始叫地主阶段")
        actionLog.push(`${landlordName} 成为地主`)
        actionLog.push("地主获得底牌，游戏开始")
      }

      // 添加历史回合信息
      if (backendState.turn_history && backendState.turn_history.length > 0) {
        backendState.turn_history.forEach((turn: any) => {
          const playerName = gameState.players.find(p => 
            p.id === `player_${turn.player.split('_')[1]}`
          )?.name || turn.player
          
          if (turn.play === "pass") {
            actionLog.push(`${playerName} 过牌`)
          } else if (turn.play && turn.play.cards) {
            const cardsStr = turn.play.cards.join(", ")
            actionLog.push(`${playerName} 出牌: ${cardsStr}`)
          }
        })
      }

      gameState.action_log = actionLog
    }

    return gameState
  }

  const handleRestart = () => {
    stopPolling()
    setGameState(null)
    setError(null)
    setCurrentGameId(null)
    setLastValidGameState(null)
  }

  if (!gameState) {
    return <WelcomeView onStartGame={startNewGame} isLoading={isLoading} error={error} />
  }

  return (
    <>
      <GameBoard gameState={gameState} />
      {gameState.winner && <EndGameModal winner={gameState.winner} onRestart={handleRestart} />}
    </>
  )
}
