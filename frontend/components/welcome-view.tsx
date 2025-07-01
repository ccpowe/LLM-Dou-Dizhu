"use client"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Loader2, Zap } from "lucide-react"

interface WelcomeViewProps {
  onStartGame: () => void
  isLoading: boolean
  error: string | null
}

export function WelcomeView({ onStartGame, isLoading, error }: WelcomeViewProps) {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <Card className="bg-gray-800 border-gray-700 p-8 max-w-md w-full text-center">
        <div className="mb-8">
          <div className="flex items-center justify-center mb-4">
            <Zap className="h-12 w-12 text-blue-400 mr-2" />
            <h1 className="text-3xl font-bold text-white">AI 斗地主</h1>
          </div>
          <h2 className="text-xl text-blue-400 mb-2">竞技观察室</h2>
          <p className="text-gray-400 text-sm">观察三个 AI 智能体进行斗地主对战</p>
        </div>

        <div className="mb-6">
          <div className="grid grid-cols-1 gap-2 text-sm text-gray-300">
            <div className="flex justify-between">
              <span>Agent 1:</span>
              <span className="text-blue-400">Gemini Pro</span>
            </div>
            <div className="flex justify-between">
              <span>Agent 2:</span>
              <span className="text-green-400">GPT-4o</span>
            </div>
            <div className="flex justify-between">
              <span>Agent 3:</span>
              <span className="text-purple-400">Claude 3</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-300 text-sm">{error}</div>
        )}

        <Button
          onClick={onStartGame}
          disabled={isLoading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              启动中...
            </>
          ) : (
            "开始新对局"
          )}
        </Button>
      </Card>
    </div>
  )
}
