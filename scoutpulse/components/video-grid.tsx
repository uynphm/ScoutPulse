"use client"

import { useState, useEffect, useMemo } from "react"
import { Play, Clock, Calendar, TrendingUp, TrendingDown, Filter } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { filterHighlightsByType, filterHighlightsByDateRange, sortHighlights, type VideoHighlight } from "@/lib/data"
import { useApp } from "@/lib/context"

interface VideoGridProps {
  highlights?: VideoHighlight[]
}

export function VideoGrid({ highlights: initialHighlights = [] }: VideoGridProps) {
  const { filters } = useApp()
  const [sortBy, setSortBy] = useState<"date" | "duration" | "relevance" | "confidence">("date")

  // Memoize the filtered highlights to prevent infinite loops
  const highlights = useMemo(() => {
    let filteredHighlights = initialHighlights

    // Filter by selected player
    if (filters.selectedPlayer !== "all") {
      filteredHighlights = filteredHighlights.filter(h => h.playerId === filters.selectedPlayer)
    }

    // Filter by strength/weakness toggles
    if (!filters.showStrengths && !filters.showWeaknesses) {
      filteredHighlights = filteredHighlights.filter(h => h.type === "neutral")
    } else if (!filters.showStrengths) {
      filteredHighlights = filteredHighlights.filter(h => h.type !== "strength")
    } else if (!filters.showWeaknesses) {
      filteredHighlights = filteredHighlights.filter(h => h.type !== "weakness")
    }

    // Filter by confidence threshold
    filteredHighlights = filteredHighlights.filter(h => h.aiInsights.confidence >= filters.confidenceThreshold)

    // Apply date range filter
    filteredHighlights = filterHighlightsByDateRange(filteredHighlights, filters.dateRange)

    // Apply sorting
    filteredHighlights = sortHighlights(filteredHighlights, sortBy)

    return filteredHighlights
  }, [initialHighlights, filters.selectedPlayer, filters.showStrengths, filters.showWeaknesses, filters.confidenceThreshold, filters.dateRange, sortBy])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Video Highlights</h2>
        <div className="flex items-center gap-2">
          <p className="text-sm text-muted-foreground">{highlights.length} clips found</p>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                <Filter className="h-4 w-4" />
                Sort
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Sort by</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setSortBy("date")}>
                Most Recent
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy("duration")}>
                Duration (Short)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy("confidence")}>
                AI Confidence
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setSortBy("relevance")}>
                Relevance
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {highlights.map((highlight) => (
          <VideoCard key={highlight.id} highlight={highlight} />
        ))}
      </div>

      {highlights.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No highlights found matching your criteria.</p>
          <Button 
            variant="outline" 
            onClick={() => {
              setSortBy("date")
            }}
            className="mt-4"
          >
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  )
}

function VideoCard({ highlight }: { highlight: VideoHighlight }) {
  return (
    <Card className="group cursor-pointer overflow-hidden transition-all hover:ring-2 hover:ring-ring">
      <div className="relative aspect-video overflow-hidden bg-muted">
        <img
          src={highlight.thumbnail || "/api/placeholder/400/225"}
          alt={highlight.title}
          className="h-full w-full object-cover transition-transform group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-black/40 opacity-0 transition-opacity group-hover:opacity-100 flex items-center justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/90">
            <Play className="h-8 w-8 text-primary-foreground fill-primary-foreground ml-1" />
          </div>
        </div>
        <div className="absolute top-2 right-2 flex items-center gap-1 rounded-md bg-black/70 px-2 py-1 text-xs text-white">
          <Clock className="h-3 w-3" />
          {highlight.duration}
        </div>
        <div className="absolute top-2 left-2">
          {highlight.type === "strength" && (
            <Badge className="bg-success text-success-foreground">
              <TrendingUp className="h-3 w-3 mr-1" />
              Strength
            </Badge>
          )}
          {highlight.type === "weakness" && (
            <Badge className="bg-destructive text-destructive-foreground">
              <TrendingDown className="h-3 w-3 mr-1" />
              Weakness
            </Badge>
          )}
          {highlight.type === "neutral" && (
            <Badge className="bg-secondary text-secondary-foreground">
              Neutral
            </Badge>
          )}
        </div>
        <div className="absolute bottom-2 right-2">
          <Badge variant="outline" className="bg-black/70 text-white border-white/30 text-xs">
            {highlight.aiInsights.confidence}% confidence
          </Badge>
        </div>
      </div>

      <CardContent className="p-4 space-y-3">
        <h3 className="font-semibold text-pretty line-clamp-2">{highlight.title}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">{highlight.description}</p>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" />
            {new Date(highlight.date).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            })}
          </div>
          <span className="text-xs">•</span>
          <span className="truncate">{highlight.match}</span>
        </div>

        <div className="flex flex-wrap gap-1.5">
          {highlight.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
