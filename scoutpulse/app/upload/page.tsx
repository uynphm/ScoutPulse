"use client"

import { useState } from "react"
import { Navbar } from "@/components/navbar"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, Video, Loader2 } from "lucide-react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function UploadPage() {
  const [videoUrl, setVideoUrl] = useState("")
  const [playerId, setPlayerId] = useState("test-player")
  const [matchName, setMatchName] = useState("")
  const [matchDate, setMatchDate] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsProcessing(true)
    setError(null)
    setResult(null)

    try {
      const normalizedMatchDate = (() => {
        if (!matchDate) {
          return new Date().toISOString()
        }

        const candidates = [matchDate, `${matchDate}:00`, `${matchDate}Z`, `${matchDate}:00Z`]

        for (const candidate of candidates) {
          const parsed = new Date(candidate)
          if (!Number.isNaN(parsed.valueOf())) {
            return parsed.toISOString()
          }
        }

        return new Date().toISOString()
      })()

      const response = await fetch(`${API_BASE_URL}/api/process-video`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_url: videoUrl,
          player_id: playerId,
          match_name: matchName || "Unnamed Match",
          match_date: normalizedMatchDate,
          auto_create_highlights: true,
        }),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Failed to process video: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-6 max-w-3xl">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Video className="h-6 w-6" />
                  Upload Match Video
                </CardTitle>
                <CardDescription>
                  Process a match video to automatically extract player highlights using AI
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="video-url">Video URL *</Label>
                    <Input
                      id="video-url"
                      type="url"
                      placeholder="https://example.com/match-video.mp4"
                      value={videoUrl}
                      onChange={(e) => setVideoUrl(e.target.value)}
                      required
                    />
                    <p className="text-sm text-muted-foreground">
                      Publicly accessible video URL (MP4, MOV, etc.)
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="player-id">Player ID *</Label>
                    <Input
                      id="player-id"
                      type="text"
                      placeholder="test-player"
                      value={playerId}
                      onChange={(e) => setPlayerId(e.target.value)}
                      required
                    />
                    <p className="text-sm text-muted-foreground">
                      Must match an existing player in the database
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="match-name">Match Name</Label>
                    <Input
                      id="match-name"
                      type="text"
                      placeholder="Team A vs Team B"
                      value={matchName}
                      onChange={(e) => setMatchName(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="match-date">Match Date</Label>
                    <Input
                      id="match-date"
                      type="datetime-local"
                      value={matchDate}
                      onChange={(e) => setMatchDate(e.target.value)}
                    />
                  </div>

                  <Button type="submit" disabled={isProcessing} className="w-full">
                    {isProcessing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing Video...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Process Video
                      </>
                    )}
                  </Button>
                </form>

                {error && (
                  <div className="mt-4 p-4 bg-destructive/10 border border-destructive rounded-md">
                    <p className="text-sm text-destructive font-medium">Error:</p>
                    <p className="text-sm text-destructive">{error}</p>
                  </div>
                )}

                {result && (
                  <div className="mt-4 p-4 bg-green-500/10 border border-green-500 rounded-md">
                    <p className="text-sm font-medium text-green-700 dark:text-green-400 mb-2">
                      ✅ Video processed successfully!
                    </p>
                    <div className="text-sm space-y-1">
                      <p>
                        <span className="font-medium">Video ID:</span> {result.video_id}
                      </p>
                      <p>
                        <span className="font-medium">Highlights Created:</span>{" "}
                        {result.highlights_created}
                      </p>
                      {result.analysis && (
                        <p>
                          <span className="font-medium">Events Detected:</span>{" "}
                          {result.analysis.events_detected?.length || 0}
                        </p>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-6 p-4 bg-muted rounded-md">
                  <p className="text-sm font-medium mb-2">ℹ️ How it works:</p>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    <li>Video uploads to Twelve Labs AI</li>
                    <li>AI analyzes and detects soccer events (goals, assists, etc.)</li>
                    <li>Highlights are automatically created in the database</li>
                    <li>View results in the main dashboard</li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
