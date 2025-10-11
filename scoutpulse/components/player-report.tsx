"use client"

import type React from "react"

import { useState } from "react"
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp, Sparkles, Target, Zap, Shield } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface PlayerStat {
  label: string
  value: number
  max: number
  icon?: React.ReactNode
}

const playerStats: PlayerStat[] = [
  { label: "Dribbling", value: 95, max: 100, icon: <Zap className="h-4 w-4" /> },
  { label: "Finishing", value: 92, max: 100, icon: <Target className="h-4 w-4" /> },
  { label: "Passing", value: 88, max: 100, icon: <Sparkles className="h-4 w-4" /> },
  { label: "Defense", value: 45, max: 100, icon: <Shield className="h-4 w-4" /> },
]

const strengths = [
  {
    title: "Exceptional Ball Control",
    description: "Maintains possession under high pressure with 94% success rate in tight spaces.",
    confidence: 98,
  },
  {
    title: "Clinical Finishing",
    description: "Converts 78% of clear chances, significantly above league average of 52%.",
    confidence: 95,
  },
  {
    title: "Vision & Creativity",
    description: "Creates 4.2 key passes per game with innovative through balls and assists.",
    confidence: 92,
  },
]

const weaknesses = [
  {
    title: "Defensive Contribution",
    description: "Limited tracking back with only 1.2 tackles per game, below position average.",
    confidence: 89,
  },
  {
    title: "Aerial Duels",
    description: "Wins only 38% of aerial challenges, a notable weakness in physical contests.",
    confidence: 85,
  },
]

export function PlayerReport() {
  const [strengthsOpen, setStrengthsOpen] = useState(true)
  const [weaknessesOpen, setWeaknessesOpen] = useState(true)

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            AI-Generated Report
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Player Overview */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center text-2xl font-bold">
                LM
              </div>
              <div>
                <h3 className="font-semibold text-lg">Lionel Messi</h3>
                <p className="text-sm text-muted-foreground">Forward • Barcelona</p>
              </div>
            </div>
          </div>

          {/* Key Stats */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Key Attributes</h4>
            {playerStats.map((stat) => (
              <div key={stat.label} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    {stat.icon}
                    <span>{stat.label}</span>
                  </div>
                  <span className="font-semibold">{stat.value}</span>
                </div>
                <Progress value={stat.value} className="h-2" />
              </div>
            ))}
          </div>

          {/* AI Summary */}
          <div className="rounded-lg bg-muted p-4 space-y-2">
            <p className="text-sm font-medium">AI Summary</p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Elite attacking player with world-class technical ability. Excels in one-on-one situations and creating
              goal-scoring opportunities. Primary weakness is defensive contribution, but offensive output more than
              compensates.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Strengths Section */}
      <Card>
        <Collapsible open={strengthsOpen} onOpenChange={setStrengthsOpen}>
          <CardHeader className="pb-3">
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-between p-0 h-auto hover:bg-transparent">
                <CardTitle className="flex items-center gap-2 text-success">
                  <TrendingUp className="h-5 w-5" />
                  Strengths ({strengths.length})
                </CardTitle>
                {strengthsOpen ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
              </Button>
            </CollapsibleTrigger>
          </CardHeader>
          <CollapsibleContent>
            <CardContent className="space-y-4 pt-0">
              {strengths.map((strength, index) => (
                <div key={index} className="space-y-2 pb-4 border-b last:border-0 last:pb-0">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-sm">{strength.title}</h4>
                    <Badge variant="outline" className="text-xs">
                      {strength.confidence}% confidence
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{strength.description}</p>
                </div>
              ))}
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      {/* Weaknesses Section */}
      <Card>
        <Collapsible open={weaknessesOpen} onOpenChange={setWeaknessesOpen}>
          <CardHeader className="pb-3">
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-between p-0 h-auto hover:bg-transparent">
                <CardTitle className="flex items-center gap-2 text-destructive">
                  <TrendingDown className="h-5 w-5" />
                  Weaknesses ({weaknesses.length})
                </CardTitle>
                {weaknessesOpen ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
              </Button>
            </CollapsibleTrigger>
          </CardHeader>
          <CollapsibleContent>
            <CardContent className="space-y-4 pt-0">
              {weaknesses.map((weakness, index) => (
                <div key={index} className="space-y-2 pb-4 border-b last:border-0 last:pb-0">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-sm">{weakness.title}</h4>
                    <Badge variant="outline" className="text-xs">
                      {weakness.confidence}% confidence
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{weakness.description}</p>
                </div>
              ))}
            </CardContent>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      {/* Match Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Recent Performance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Goals (Last 10 games)</span>
            <span className="font-semibold">12</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Assists (Last 10 games)</span>
            <span className="font-semibold">8</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Average Rating</span>
            <span className="font-semibold">8.7/10</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Minutes Played</span>
            <span className="font-semibold">847</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
