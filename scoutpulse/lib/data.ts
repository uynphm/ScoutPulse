// Data transformation utilities
import { apiClient, Player as ApiPlayer, VideoHighlight as ApiVideoHighlight } from './api'

// Transform API Player to Frontend Player format
function transformPlayer(apiPlayer: ApiPlayer | null): Player | null {
  if (!apiPlayer) return null
  
  return {
    id: apiPlayer.id,
    name: apiPlayer.name,
    position: apiPlayer.position,
    team: apiPlayer.team,
    age: apiPlayer.age,
    nationality: apiPlayer.nationality,
    avatar: apiPlayer.avatar ?? undefined,
    stats: {
      dribbling: apiPlayer.stats.dribbling ?? 0,
      finishing: apiPlayer.stats.finishing ?? 0,
      passing: apiPlayer.stats.passing ?? 0,
      defense: apiPlayer.stats.defense ?? 0,
      speed: apiPlayer.stats.speed ?? 0,
      strength: apiPlayer.stats.strength ?? 0,
    },
    recentPerformance: {
      goals: apiPlayer.recent_performance.goals,
      assists: apiPlayer.recent_performance.assists,
      averageRating: apiPlayer.recent_performance.average_rating,
      minutesPlayed: apiPlayer.recent_performance.minutes_played,
    }
  }
}

// Transform API VideoHighlight to Frontend VideoHighlight format
function transformVideoHighlight(apiHighlight: ApiVideoHighlight | null): VideoHighlight | null {
  if (!apiHighlight) return null
  
  return {
    id: apiHighlight.id,
    title: apiHighlight.title,
    thumbnail: apiHighlight.thumbnail,
    videoUrl: apiHighlight.video_url,
    duration: apiHighlight.duration,
    match: apiHighlight.match,
    date: apiHighlight.date,
    type: apiHighlight.type,
    tags: apiHighlight.tags,
    playerId: apiHighlight.player_id,
    description: apiHighlight.description,
    timestamp: apiHighlight.timestamp,
    aiInsights: {
      confidence: apiHighlight.ai_insights.confidence,
      analysis: apiHighlight.ai_insights.analysis,
      keyMoments: apiHighlight.ai_insights.key_moments,
    }
  }
}

// Define frontend interfaces for type safety
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

// API-based data functions
export async function getPlayers(): Promise<Player[]> {
  try {
    const apiPlayers = await apiClient.getPlayers()
    return apiPlayers.map(transformPlayer).filter((p): p is Player => p !== null)
  } catch (error) {
    console.error('Failed to fetch players:', error)
    return []
  }
}

export async function getPlayerById(id: string): Promise<Player | null> {
  try {
    const apiPlayer = await apiClient.getPlayerById(id)
    return transformPlayer(apiPlayer)
  } catch (error) {
    console.error(`Failed to fetch player ${id}:`, error)
    return null
  }
}

export async function getHighlightsByPlayerId(playerId: string): Promise<VideoHighlight[]> {
  try {
    const apiHighlights = await apiClient.getHighlights(playerId)
    return apiHighlights.map(transformVideoHighlight).filter((h): h is VideoHighlight => h !== null)
  } catch (error) {
    console.error(`Failed to fetch highlights for player ${playerId}:`, error)
    return []
  }
}

export async function getHighlightById(id: string): Promise<VideoHighlight | null> {
  try {
    const apiHighlight = await apiClient.getHighlightById(id)
    return transformVideoHighlight(apiHighlight)
  } catch (error) {
    console.error(`Failed to fetch highlight ${id}:`, error)
    return null
  }
}

export async function searchPlayers(query: string): Promise<Player[]> {
  try {
    const searchResults = await apiClient.search(query, 'players')
    // For now, we'll need to fetch each player individually since search returns SearchResult
    // In a real app, you might want to modify the API to return full player objects
    const players: (Player | null)[] = []
    for (const result of searchResults) {
      if (result.type === 'player') {
        const player = await getPlayerById(result.id)
        players.push(player)
      }
    }
    return players.filter((p): p is Player => p !== null)
  } catch (error) {
    console.error(`Failed to search players with query "${query}":`, error)
    return []
  }
}

export async function searchHighlights(query: string): Promise<VideoHighlight[]> {
  try {
    const searchResults = await apiClient.search(query, 'highlights')
    // Similar to searchPlayers, we'll fetch each highlight individually
    const highlights: (VideoHighlight | null)[] = []
    for (const result of searchResults) {
      if (result.type === 'highlight') {
        const highlight = await getHighlightById(result.id)
        highlights.push(highlight)
      }
    }
    return highlights.filter((h): h is VideoHighlight => h !== null)
  } catch (error) {
    console.error(`Failed to search highlights with query "${query}":`, error)
    return []
  }
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
