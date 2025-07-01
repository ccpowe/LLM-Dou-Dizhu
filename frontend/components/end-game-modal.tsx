"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Trophy, Users } from "lucide-react"

interface EndGameModalProps {
  winner: "landlord" | "farmers"
  onRestart: () => void
}

export function EndGameModal({ winner, onRestart }: EndGameModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <Card className="bg-gray-800 border-gray-700 p-8 max-w-md w-full text-center">
        <div className="mb-6">
          {winner === "landlord" ? (
            <Trophy className="h-16 w-16 text-yellow-400 mx-auto mb-4" />
          ) : (
            <Users className="h-16 w-16 text-green-400 mx-auto mb-4" />
          )}

          <h2 className="text-3xl font-bold text-white mb-2">{winner === "landlord" ? "地主胜利！" : "农民胜利！"}</h2>

          <p className="text-gray-400">{winner === "landlord" ? "地主成功出完所有手牌" : "农民联盟成功阻止地主"}</p>
        </div>

        <Button onClick={onRestart} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3">
          再来一局
        </Button>
      </Card>
    </div>
  )
}
