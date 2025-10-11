"use client"

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

interface VideoHighlight {
  id: string
  title: string
  thumbnail: string
  duration: string
  match: string
  date: string
  type: "strength" | "weakness" | "neutral"
  tags: string[]
}

const mockHighlights: VideoHighlight[] = [
  {
    id: "1",
    title: "Exceptional Dribbling vs Real Madrid",
    thumbnail: "/soccer-player-dribbling.png",
    duration: "0:45",
    match: "Barcelona vs Real Madrid",
    date: "2024-03-15",
    type: "strength",
    tags: ["Dribbling", "Ball Control", "Speed"],
  },
  {
    id: "2",
    title: "Clinical Finishing - Hat Trick Goals",
    thumbnail: "/soccer-goal-celebration.png",
    duration: "1:20",
    match: "Barcelona vs Sevilla",
    date: "2024-03-10",
    type: "strength",
    tags: ["Finishing", "Positioning", "Shooting"],
  },
  {
    id: "3",
    title: "Defensive Positioning Issues",
    thumbnail: "/soccer-defensive-play.jpg",
    duration: "0:35",
    match: "Barcelona vs Atletico",
    date: "2024-03-05",
    type: "weakness",
    tags: ["Defense", "Positioning", "Tracking"],
  },
  {
    id: "4",
    title: "Perfect Through Ball Assists",
    thumbnail: "/soccer-pass-assist.jpg",
    duration: "1:05",
    match: "Barcelona vs Valencia",
    date: "2024-02-28",
    type: "strength",
    tags: ["Passing", "Vision", "Assists"],
  },
  {
    id: "5",
    title: "Missed Penalty Opportunities",
    thumbnail: "/soccer-penalty-kick.png",
    duration: "0:28",
    match: "Barcelona vs Villarreal",
    date: "2024-02-20",
    type: "weakness",
    tags: ["Penalties", "Pressure", "Composure"],
  },
  {
    id: "6",
    title: "Free Kick Masterclass",
    thumbnail: "/soccer-free-kick.jpg",
    duration: "0:52",
    match: "Barcelona vs Athletic Bilbao",
    date: "2024-02-15",
    type: "strength",
    tags: ["Free Kicks", "Technique", "Accuracy"],
  },
]

export function VideoGrid() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Video Highlights</h2>
        <div className="flex items-center gap-2">
          <p className="text-sm text-muted-foreground">{mockHighlights.length} clips found</p>
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
              <DropdownMenuItem>Most Recent</DropdownMenuItem>
              <DropdownMenuItem>Oldest First</DropdownMenuItem>
              <DropdownMenuItem>Duration (Short)</DropdownMenuItem>
              <DropdownMenuItem>Duration (Long)</DropdownMenuItem>
              <DropdownMenuItem>Relevance</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockHighlights.map((highlight) => (
          <VideoCard key={highlight.id} highlight={highlight} />
        ))}
      </div>
    </div>
  )
}

function VideoCard({ highlight }: { highlight: VideoHighlight }) {
  return (
    <Card className="group cursor-pointer overflow-hidden transition-all hover:ring-2 hover:ring-ring">
      <div className="relative aspect-video overflow-hidden bg-muted">
        <img
          src={highlight.thumbnail || "/placeholder.svg"}
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
        </div>
      </div>

      <CardContent className="p-4 space-y-3">
        <h3 className="font-semibold text-pretty line-clamp-2">{highlight.title}</h3>

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
