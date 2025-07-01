interface CardComponentProps {
  cardCode: string
  isFaceUp: boolean
}

export function CardComponent({ cardCode, isFaceUp }: CardComponentProps) {
  const parseCard = (code: string) => {
    if (code === "BJ") return { suit: "🃏", rank: "小", color: "text-gray-900" }
    if (code === "RJ") return { suit: "🃏", rank: "大", color: "text-red-500" }

    const suit = code[0]
    const rank = code.slice(1)

    const suitMap: { [key: string]: string } = {
      S: "♠️",
      H: "♥️",
      D: "♦️",
      C: "♣️",
    }

    const colorMap: { [key: string]: string } = {
      S: "text-gray-900",
      H: "text-red-500",
      D: "text-red-500",
      C: "text-gray-900",
    }

    return {
      suit: suitMap[suit] || suit,
      rank: rank,
      color: colorMap[suit] || "text-gray-900",
    }
  }

  if (!isFaceUp) {
    return (
      <div className="w-12 h-16 bg-blue-900 border border-blue-700 rounded flex items-center justify-center">
        <div className="w-8 h-10 bg-blue-800 rounded-sm"></div>
      </div>
    )
  }

  const { suit, rank, color } = parseCard(cardCode)

  return (
    <div className="w-12 h-16 bg-white border border-gray-300 rounded flex flex-col items-center justify-center text-xs font-bold shadow-sm">
      <div className={color}>{suit}</div>
      <div className={color}>{rank}</div>
    </div>
  )
}
