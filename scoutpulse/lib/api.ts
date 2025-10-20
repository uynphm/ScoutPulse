const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE"

async function request<T>(
  path: string,
  method: HttpMethod = "GET",
  body?: unknown,
  fallback?: T
): Promise<T> {
  const init: RequestInit = {
    method,
    cache: "no-store",
    ...(body !== undefined
      ? {
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        }
      : {}),
  }

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, init)
  } catch (error) {
    if (fallback !== undefined) return fallback
    throw new Error(`Network request to ${path} failed: ${(error as Error).message}`)
  }

  if (!response.ok) {
    if (fallback !== undefined && (response.status === 404 || response.status === 204 || response.status === 422)) {
      return fallback
    }

    const text = await response.text().catch(() => "")
    throw new Error(`API ${method} ${path} failed (${response.status} ${response.statusText}): ${text}`)
  }

  if (response.status === 204) {
    if (fallback !== undefined) return fallback
    return undefined as T
  }

  return response.json() as Promise<T>
}

export interface Player {
  id: string
  name: string
  position: string
  team: string
  age: number
  nationality: string
  avatar?: string | null
  stats: Record<string, number>
  recent_performance: {
    goals: number
    assists: number
    average_rating: number
    minutes_played: number
  }
}

export interface VideoHighlight {
  id: string
  title: string
  thumbnail: string
  video_url: string
  duration: string
  match: string
  date: string
  type: "strength" | "weakness" | "neutral"
  tags: string[]
  player_id: string
  description: string
  timestamp: {
    start: number
    end: number
  }
  ai_insights: {
    confidence: number
    analysis: string
    key_moments: string[]
  }
}

export interface SearchResult {
  type: "player" | "highlight" | "match"
  id: string
  title: string
  description: string
  relevance_score: number
}

async function getPlayers(): Promise<Player[]> {
  return request<Player[]>("/api/players", "GET", undefined, [])
}

async function getPlayerById(id: string): Promise<Player | null> {
  return request<Player | null>(`/api/players/${id}`, "GET", undefined, null)
}

async function getHighlights(playerId?: string): Promise<VideoHighlight[]> {
  const query = playerId ? `?player_id=${encodeURIComponent(playerId)}` : ""
  return request<VideoHighlight[]>(`/api/highlights${query}`, "GET", undefined, [])
}

async function getHighlightById(id: string): Promise<VideoHighlight | null> {
  return request<VideoHighlight | null>(`/api/highlights/${id}`, "GET", undefined, null)
}

async function search(query: string, type: "players" | "highlights" | "all" = "all"): Promise<SearchResult[]> {
  const params = new URLSearchParams({ q: query, search_type: type })
  return request<SearchResult[]>(`/api/search?${params.toString()}`, "GET", undefined, [])
}

export const apiClient = {
  getPlayers,
  getPlayerById,
  getHighlights,
  getHighlightById,
  search,
}

export type ApiClient = typeof apiClient
