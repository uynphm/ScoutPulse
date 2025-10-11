export interface Player {
  id: string
  name: string
  position: string
  team: string
  age: number
  nationality: string
  avatar?: string
  stats: {
    dribbling: number
    finishing: number
    passing: number
    defense: number
    speed: number
    strength: number
  }
  recentPerformance: {
    goals: number
    assists: number
    averageRating: number
    minutesPlayed: number
  }
}

export interface VideoHighlight {
  id: string
  title: string
  thumbnail: string
  videoUrl: string
  duration: string
  match: string
  date: string
  type: "strength" | "weakness" | "neutral"
  tags: string[]
  playerId: string
  description: string
  timestamp: {
    start: number
    end: number
  }
  aiInsights: {
    confidence: number
    analysis: string
    keyMoments: string[]
  }
}

export interface SearchResult {
  type: "player" | "highlight" | "match"
  id: string
  title: string
  description: string
  relevanceScore: number
}

// Mock data
export const players: Player[] = [
  {
    id: "messi",
    name: "Lionel Messi",
    position: "Forward",
    team: "Barcelona",
    age: 36,
    nationality: "Argentina",
    stats: {
      dribbling: 95,
      finishing: 92,
      passing: 88,
      defense: 45,
      speed: 85,
      strength: 70,
    },
    recentPerformance: {
      goals: 12,
      assists: 8,
      averageRating: 8.7,
      minutesPlayed: 847,
    },
  },
  {
    id: "ronaldo",
    name: "Cristiano Ronaldo",
    position: "Forward",
    team: "Al Nassr",
    age: 39,
    nationality: "Portugal",
    stats: {
      dribbling: 88,
      finishing: 95,
      passing: 82,
      defense: 50,
      speed: 90,
      strength: 95,
    },
    recentPerformance: {
      goals: 15,
      assists: 5,
      averageRating: 8.5,
      minutesPlayed: 920,
    },
  },
  {
    id: "mbappe",
    name: "Kylian Mbappé",
    position: "Forward",
    team: "Real Madrid",
    age: 25,
    nationality: "France",
    stats: {
      dribbling: 90,
      finishing: 88,
      passing: 75,
      defense: 40,
      speed: 95,
      strength: 75,
    },
    recentPerformance: {
      goals: 18,
      assists: 6,
      averageRating: 8.8,
      minutesPlayed: 890,
    },
  },
  {
    id: "haaland",
    name: "Erling Haaland",
    position: "Forward",
    team: "Manchester City",
    age: 24,
    nationality: "Norway",
    stats: {
      dribbling: 75,
      finishing: 95,
      passing: 70,
      defense: 35,
      speed: 85,
      strength: 90,
    },
    recentPerformance: {
      goals: 22,
      assists: 3,
      averageRating: 8.9,
      minutesPlayed: 780,
    },
  },
]

export const videoHighlights: VideoHighlight[] = [
  {
    id: "1",
    title: "Exceptional Dribbling vs Real Madrid",
    thumbnail: "/api/placeholder/400/225",
    videoUrl: "/videos/messi-dribbling-1.mp4",
    duration: "0:45",
    match: "Barcelona vs Real Madrid",
    date: "2024-03-15",
    type: "strength",
    tags: ["Dribbling", "Ball Control", "Speed"],
    playerId: "messi",
    description: "Messi showcases his exceptional dribbling ability, beating multiple defenders in tight spaces.",
    timestamp: { start: 120, end: 165 },
    aiInsights: {
      confidence: 98,
      analysis: "Exceptional ball control under pressure with 94% success rate in tight spaces.",
      keyMoments: ["Initial touch", "Change of direction", "Acceleration past defender"],
    },
  },
  {
    id: "2",
    title: "Clinical Finishing - Hat Trick Goals",
    thumbnail: "/api/placeholder/400/225",
    videoUrl: "/videos/messi-finishing-1.mp4",
    duration: "1:20",
    match: "Barcelona vs Sevilla",
    date: "2024-03-10",
    type: "strength",
    tags: ["Finishing", "Positioning", "Shooting"],
    playerId: "messi",
    description: "Three clinical finishes showcasing Messi's composure in front of goal.",
    timestamp: { start: 45, end: 125 },
    aiInsights: {
      confidence: 95,
      analysis: "Converts 78% of clear chances, significantly above league average of 52%.",
      keyMoments: ["First goal - left foot", "Second goal - right foot", "Third goal - chip"],
    },
  },
  {
    id: "3",
    title: "Defensive Positioning Issues",
    thumbnail: "/api/placeholder/400/225",
    videoUrl: "/videos/messi-defense-1.mp4",
    duration: "0:35",
    match: "Barcelona vs Atletico",
    date: "2024-03-05",
    type: "weakness",
    tags: ["Defense", "Positioning", "Tracking"],
    playerId: "messi",
    description: "Examples of defensive positioning that could be improved.",
    timestamp: { start: 200, end: 235 },
    aiInsights: {
      confidence: 89,
      analysis: "Limited tracking back with only 1.2 tackles per game, below position average.",
      keyMoments: ["Missed interception", "Poor positioning", "Late tracking"],
    },
  },
  {
    id: "4",
    title: "Perfect Through Ball Assists",
    thumbnail: "/api/placeholder/400/225",
    videoUrl: "/videos/messi-passing-1.mp4",
    duration: "1:05",
    match: "Barcelona vs Valencia",
    date: "2024-02-28",
    type: "strength",
    tags: ["Passing", "Vision", "Assists"],
    playerId: "messi",
    description: "Two perfectly weighted through balls leading to goals.",
    timestamp: { start: 80, end: 145 },
    aiInsights: {
      confidence: 92,
      analysis: "Creates 4.2 key passes per game with innovative through balls and assists.",
      keyMoments: ["First assist - through ball", "Second assist - lobbed pass"],
    },
  },
]

// Search functionality
export function searchPlayers(query: string): Player[] {
  const lowercaseQuery = query.toLowerCase()
  return players.filter(
    (player) =>
      player.name.toLowerCase().includes(lowercaseQuery) ||
      player.team.toLowerCase().includes(lowercaseQuery) ||
      player.position.toLowerCase().includes(lowercaseQuery) ||
      player.nationality.toLowerCase().includes(lowercaseQuery)
  )
}

export function searchHighlights(query: string): VideoHighlight[] {
  const lowercaseQuery = query.toLowerCase()
  return videoHighlights.filter(
    (highlight) =>
      highlight.title.toLowerCase().includes(lowercaseQuery) ||
      highlight.match.toLowerCase().includes(lowercaseQuery) ||
      highlight.tags.some((tag) => tag.toLowerCase().includes(lowercaseQuery)) ||
      highlight.description.toLowerCase().includes(lowercaseQuery)
  )
}

export function getPlayerById(id: string): Player | undefined {
  return players.find((player) => player.id === id)
}

export function getHighlightsByPlayerId(playerId: string): VideoHighlight[] {
  return videoHighlights.filter((highlight) => highlight.playerId === playerId)
}

export function getHighlightById(id: string): VideoHighlight | undefined {
  return videoHighlights.find((highlight) => highlight.id === id)
}

// Filter functions
export function filterHighlightsByType(
  highlights: VideoHighlight[],
  type: "strength" | "weakness" | "neutral" | "all"
): VideoHighlight[] {
  if (type === "all") return highlights
  return highlights.filter((highlight) => highlight.type === type)
}

export function filterHighlightsByDateRange(
  highlights: VideoHighlight[],
  range: "week" | "month" | "season" | "year" | "all"
): VideoHighlight[] {
  if (range === "all") return highlights

  const now = new Date()
  const cutoffDate = new Date()

  switch (range) {
    case "week":
      cutoffDate.setDate(now.getDate() - 7)
      break
    case "month":
      cutoffDate.setMonth(now.getMonth() - 1)
      break
    case "season":
      cutoffDate.setMonth(now.getMonth() - 6)
      break
    case "year":
      cutoffDate.setFullYear(now.getFullYear() - 1)
      break
  }

  return highlights.filter((highlight) => new Date(highlight.date) >= cutoffDate)
}

export function sortHighlights(
  highlights: VideoHighlight[],
  sortBy: "date" | "duration" | "relevance" | "confidence"
): VideoHighlight[] {
  return [...highlights].sort((a, b) => {
    switch (sortBy) {
      case "date":
        return new Date(b.date).getTime() - new Date(a.date).getTime()
      case "duration":
        return parseInt(a.duration.replace(":", "")) - parseInt(b.duration.replace(":", ""))
      case "confidence":
        return b.aiInsights.confidence - a.aiInsights.confidence
      case "relevance":
        return b.aiInsights.confidence - a.aiInsights.confidence
      default:
        return 0
    }
  })
}
