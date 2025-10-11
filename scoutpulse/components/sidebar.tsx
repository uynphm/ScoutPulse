"use client"

import { useState } from "react"
import { Filter, Users, BarChart3, Video, TrendingUp, TrendingDown, Calendar, Trophy } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Slider } from "@/components/ui/slider"

export function Sidebar() {
  const [showStrengths, setShowStrengths] = useState(true)
  const [showWeaknesses, setShowWeaknesses] = useState(true)
  const [confidenceThreshold, setConfidenceThreshold] = useState([75])

  return (
    <aside className="w-72 border-r border-border bg-card p-6 overflow-y-auto">
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </h2>

          <div className="space-y-4">
            <div>
              <Label htmlFor="player-select" className="text-sm font-medium mb-2 block">
                Select Player
              </Label>
              <Select defaultValue="messi">
                <SelectTrigger id="player-select">
                  <SelectValue placeholder="Choose a player" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="messi">Lionel Messi</SelectItem>
                  <SelectItem value="ronaldo">Cristiano Ronaldo</SelectItem>
                  <SelectItem value="mbappe">Kylian Mbappé</SelectItem>
                  <SelectItem value="haaland">Erling Haaland</SelectItem>
                  <SelectItem value="salah">Mohamed Salah</SelectItem>
                  <SelectItem value="debruyne">Kevin De Bruyne</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label htmlFor="strengths" className="flex items-center gap-2 text-sm">
                  <TrendingUp className="h-4 w-4 text-success" />
                  Show Strengths
                </Label>
                <Switch id="strengths" checked={showStrengths} onCheckedChange={setShowStrengths} />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="weaknesses" className="flex items-center gap-2 text-sm">
                  <TrendingDown className="h-4 w-4 text-destructive" />
                  Show Weaknesses
                </Label>
                <Switch id="weaknesses" checked={showWeaknesses} onCheckedChange={setShowWeaknesses} />
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <Label htmlFor="confidence" className="text-sm font-medium">
                AI Confidence Threshold: {confidenceThreshold[0]}%
              </Label>
              <Slider
                id="confidence"
                value={confidenceThreshold}
                onValueChange={setConfidenceThreshold}
                max={100}
                step={5}
                className="py-2"
              />
              <p className="text-xs text-muted-foreground">Only show insights above this confidence level</p>
            </div>

            <Separator />

            <div>
              <Label htmlFor="date-range" className="text-sm font-medium mb-2 block">
                Match Date Range
              </Label>
              <Select defaultValue="all">
                <SelectTrigger id="date-range">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Time</SelectItem>
                  <SelectItem value="week">Last Week</SelectItem>
                  <SelectItem value="month">Last Month</SelectItem>
                  <SelectItem value="season">This Season</SelectItem>
                  <SelectItem value="year">Last Year</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            <div>
              <Label htmlFor="competition" className="text-sm font-medium mb-2 block">
                Competition
              </Label>
              <Select defaultValue="all">
                <SelectTrigger id="competition">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Competitions</SelectItem>
                  <SelectItem value="laliga">La Liga</SelectItem>
                  <SelectItem value="ucl">Champions League</SelectItem>
                  <SelectItem value="copa">Copa del Rey</SelectItem>
                  <SelectItem value="international">International</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            <div>
              <Label htmlFor="playback-speed" className="text-sm font-medium mb-2 block">
                Playback Speed
              </Label>
              <Select defaultValue="1">
                <SelectTrigger id="playback-speed">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0.5">0.5x</SelectItem>
                  <SelectItem value="0.75">0.75x</SelectItem>
                  <SelectItem value="1">1x (Normal)</SelectItem>
                  <SelectItem value="1.25">1.25x</SelectItem>
                  <SelectItem value="1.5">1.5x</SelectItem>
                  <SelectItem value="2">2x</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Separator />

        <nav className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Navigation</h3>
          <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-accent">
            <Users className="h-4 w-4" />
            Players
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-accent">
            <Video className="h-4 w-4" />
            Highlights
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-accent">
            <BarChart3 className="h-4 w-4" />
            Reports
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-accent">
            <Trophy className="h-4 w-4" />
            Teams
          </Button>
          <Button variant="ghost" className="w-full justify-start gap-2 hover:bg-accent">
            <Calendar className="h-4 w-4" />
            Matches
          </Button>
        </nav>

        <Separator />

        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Quick Actions</h3>
          <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
            Export Report
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
            Compare Players
          </Button>
          <Button variant="outline" size="sm" className="w-full justify-start bg-transparent">
            Save Search
          </Button>
        </div>
      </div>
    </aside>
  )
}
