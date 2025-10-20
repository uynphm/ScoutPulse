"use client"

import { useState, useRef, useMemo } from "react"
import { Play, Pause, Volume2, VolumeX, Maximize, SkipBack, SkipForward } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface VideoPlayerProps {
  videoUrl?: string
  posterUrl?: string
  title: string
  match: string
  insights?: {
    type: "strength" | "weakness" | "neutral"
    text: string
    timestamp: string
  }[]
}

function getYouTubeIdFromUrl(url?: string): string | null {
  if (!url) {
    return null
  }

  try {
    const parsed = new URL(url)
    const host = parsed.hostname || ""

    if (host.includes("youtu.be")) {
      return parsed.pathname.replace("/", "") || null
    }

    if (host.includes("youtube")) {
      if (parsed.pathname.startsWith("/embed/")) {
        const [, , id] = parsed.pathname.split("/")
        return id || null
      }

      if (parsed.pathname.startsWith("/shorts/")) {
        const [, , id] = parsed.pathname.split("/")
        return id || null
      }

      const searchId = parsed.searchParams.get("v")
      if (searchId) {
        return searchId
      }
    }
  } catch (error) {
    return null
  }

  return null
}

function buildYouTubeEmbedUrl(videoId: string): string {
  return `https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1&playsinline=1`
}

function buildYouTubePosterUrl(videoId: string): string {
  return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
}

export function VideoPlayer({ videoUrl, posterUrl, title, match, insights = [] }: VideoPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(100)
  const videoRef = useRef<HTMLVideoElement>(null)

  const youtubeId = useMemo(() => getYouTubeIdFromUrl(videoUrl), [videoUrl])
  const isYouTube = Boolean(youtubeId)
  const youtubeEmbedUrl = useMemo(() => (youtubeId ? buildYouTubeEmbedUrl(youtubeId) : undefined), [youtubeId])
  const posterSrc = useMemo(() => {
    if (youtubeId) {
      return buildYouTubePosterUrl(youtubeId)
    }

    if (posterUrl) {
      return posterUrl
    }

    if (videoUrl && videoUrl.endsWith(".mp4")) {
      const filename = videoUrl.split("/").pop()
      if (filename) {
        const basename = filename.replace(/\.mp4$/, "")
        return `/thumbnails/${basename}.jpg`
      }
    }

    return "https://dummyimage.com/1280x720/111827/ffffff&text=Video"
  }, [youtubeId, posterUrl, videoUrl])

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }

  const handleSeek = (value: number[]) => {
    if (videoRef.current) {
      videoRef.current.currentTime = value[0]
      setCurrentTime(value[0])
    }
  }

  const skipTime = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime += seconds
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, "0")}`
  }

  return (
    <Card className="overflow-hidden">
      <div className="relative aspect-video bg-black">
        {isYouTube && youtubeEmbedUrl ? (
          <iframe
            src={youtubeEmbedUrl}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
            allowFullScreen
            className="h-full w-full"
          />
        ) : (
          <>
            <video
              ref={videoRef}
              className="h-full w-full"
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              poster={posterSrc}
            >
              {videoUrl && <source src={videoUrl} type="video/mp4" />}
            </video>

            {/* Video Overlay Controls */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 hover:opacity-100 transition-opacity">
              <div className="absolute bottom-0 left-0 right-0 p-4 space-y-3">
                {/* Progress Bar */}
                <Slider
                  value={[currentTime]}
                  max={duration}
                  step={0.1}
                  onValueChange={handleSeek}
                  className="cursor-pointer"
                />

                {/* Controls */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Button size="icon" variant="ghost" onClick={togglePlay} className="text-white hover:bg-white/20">
                      {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5 ml-0.5" />}
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => skipTime(-10)}
                      className="text-white hover:bg-white/20"
                    >
                      <SkipBack className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => skipTime(10)}
                      className="text-white hover:bg-white/20"
                    >
                      <SkipForward className="h-4 w-4" />
                    </Button>
                    <span className="text-sm text-white font-mono">
                      {formatTime(currentTime)} / {formatTime(duration)}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button size="icon" variant="ghost" onClick={toggleMute} className="text-white hover:bg-white/20">
                      {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
                    </Button>
                    <Button size="icon" variant="ghost" className="text-white hover:bg-white/20">
                      <Maximize className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* AI Insights Overlay */}
        {insights.length > 0 && (
          <div className="absolute top-4 left-4 right-4 space-y-2">
            {insights.map((insight, index) => (
              <Badge
                key={index}
                className={
                  insight.type === "strength"
                    ? "bg-success/90 text-success-foreground"
                    : insight.type === "weakness"
                    ? "bg-destructive/90 text-destructive-foreground"
                    : "bg-muted/90 text-muted-foreground"
                }
              >
                {insight.timestamp} - {insight.text}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <CardContent className="p-4 space-y-2">
        <h3 className="font-semibold text-lg text-pretty">{title}</h3>
        <p className="text-sm text-muted-foreground">{match}</p>
      </CardContent>
    </Card>
  )
}
