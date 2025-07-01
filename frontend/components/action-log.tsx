import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useEffect, useRef } from "react"

interface ActionLogProps {
  logEntries: string[]
}

export function ActionLog({ logEntries }: ActionLogProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  // 自动滚动到最新日志
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [logEntries])

  return (
    <Card className="bg-gray-800 border-gray-700 h-full flex flex-col">
      <div className="p-4 border-b border-gray-700 flex-shrink-0">
        <h3 className="font-semibold text-white">行动日志</h3>
        <div className="text-xs text-gray-500 mt-1">共 {logEntries.length} 条记录</div>
      </div>
      
      <div className="flex-1 layout-constrained">
        <ScrollArea ref={scrollAreaRef} className="h-full action-log-scroll">
          <div className="p-4">
            <div className="space-y-2">
              {logEntries.map((entry, index) => (
                <div 
                  key={index} 
                  className="text-sm text-gray-300 p-2 bg-gray-900/50 rounded border-l-2 border-transparent hover:border-blue-400 status-transition"
                >
                  <span className="text-gray-500 text-xs font-mono">
                    {String(index + 1).padStart(2, "0")}:
                  </span>
                  <span className="ml-2">{entry}</span>
                  
                  {/* 添加时间戳显示（可选） */}
                  <div className="text-xs text-gray-600 mt-1">
                    {new Date().toLocaleTimeString('zh-CN', { 
                      hour12: false, 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
              ))}
              
              {/* 如果没有日志条目，显示占位符 */}
              {logEntries.length === 0 && (
                <div className="text-center text-gray-500 text-sm py-8">
                  <div className="game-status-indicator">
                    暂无行动记录
                  </div>
                  <div className="text-xs text-gray-600 mt-2">
                    游戏开始后将显示详细的行动日志
                  </div>
                </div>
              )}
            </div>
          </div>
        </ScrollArea>
      </div>
    </Card>
  )
}
