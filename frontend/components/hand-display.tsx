import { CardComponent } from "@/components/card-component"

interface HandDisplayProps {
  cards: string[]
  showCards: boolean
  cardCount: number
}

export function HandDisplay({ cards, showCards, cardCount }: HandDisplayProps) {
  if (!showCards) {
    // Show card backs
    return (
      <div className="cards-container">
        <div className="cards-grid">
          {Array.from({ length: Math.min(cardCount, 10) }).map((_, index) => (
            <div key={index} className="card-hover">
              <CardComponent cardCode="" isFaceUp={false} />
            </div>
          ))}
          {cardCount > 10 && (
            <div className="flex items-center justify-center w-12 h-16 bg-gray-700 rounded text-xs text-gray-400 card-hover">
              +{cardCount - 10}
            </div>
          )}
        </div>
      </div>
    )
  }

  // 显示真实扑克牌
  return (
    <div className="w-full">
      {cards.length > 0 ? (
        <div className="cards-container">
          <div className="cards-grid">
            {cards.map((cardCode, index) => (
              <div key={`${cardCode}-${index}`} className="card-hover">
                <CardComponent cardCode={cardCode} isFaceUp={true} />
              </div>
            ))}
          </div>
        </div>
      ) : (
        // 如果没有扑克牌数据，显示占位符
        <div className="cards-container">
          <div className="cards-grid">
            {Array.from({ length: Math.min(cardCount, 17) }).map((_, index) => (
              <div 
                key={index} 
                className="w-8 h-12 bg-blue-600 rounded border border-blue-500 flex items-center justify-center text-xs text-white card-hover"
              >
                ?
              </div>
            ))}
            {cardCount > 17 && (
              <div className="flex items-center justify-center w-8 h-12 bg-gray-700 rounded text-xs text-gray-400 card-hover">
                +{cardCount - 17}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
