"use client"

import { useState } from "react"
import { Search, X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { searchPlayers, searchHighlights, type SearchResult } from "@/lib/data"

export function SearchSection() {
  const [query, setQuery] = useState("")
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }

    setIsSearching(true)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const players = searchPlayers(searchQuery)
    const highlights = searchHighlights(searchQuery)
    
    const results: SearchResult[] = [
      ...players.map(player => ({
        type: "player" as const,
        id: player.id,
        title: player.name,
        description: `${player.position} • ${player.team}`,
        relevanceScore: 95
      })),
      ...highlights.map(highlight => ({
        type: "highlight" as const,
        id: highlight.id,
        title: highlight.title,
        description: `${highlight.match} • ${highlight.date}`,
        relevanceScore: highlight.aiInsights.confidence
      }))
    ]
    
    // Sort by relevance
    results.sort((a, b) => b.relevanceScore - a.relevanceScore)
    
    setSearchResults(results.slice(0, 5)) // Show top 5 results
    setIsSearching(false)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)
    
    // Debounced search
    const timeoutId = setTimeout(() => {
      handleSearch(value)
    }, 300)
    
    return () => clearTimeout(timeoutId)
  }

  const clearSearch = () => {
    setQuery("")
    setSearchResults([])
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-balance">AI-Powered Player Analysis</h1>
        <p className="text-muted-foreground text-pretty">
          Search for any player action, strength, or weakness using natural language
        </p>
      </div>

      <div className="relative">
        <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Try: 'Show Messi's best dribbles' or 'Find defensive weaknesses'..."
          className="w-full pl-12 pr-12 h-14 text-lg bg-card"
          value={query}
          onChange={handleInputChange}
        />
        {query && (
          <Button
            variant="ghost"
            size="icon"
            onClick={clearSearch}
            className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            {isSearching ? "Searching..." : `${searchResults.length} results found`}
          </p>
          <div className="space-y-2">
            {searchResults.map((result) => (
              <div
                key={`${result.type}-${result.id}`}
                className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 cursor-pointer transition-colors"
              >
                <div className="space-y-1">
                  <h3 className="font-medium">{result.title}</h3>
                  <p className="text-sm text-muted-foreground">{result.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    {result.type}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    {result.relevanceScore}% match
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Search Suggestions */}
      {!query && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Popular searches:</p>
          <div className="flex flex-wrap gap-2">
            {[
              "Messi dribbling skills",
              "Defensive weaknesses",
              "Goal scoring ability",
              "Passing accuracy",
              "Speed and agility"
            ].map((suggestion) => (
              <Button
                key={suggestion}
                variant="outline"
                size="sm"
                onClick={() => {
                  setQuery(suggestion)
                  handleSearch(suggestion)
                }}
                className="text-xs"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
