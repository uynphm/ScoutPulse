import { Navbar } from "@/components/navbar"
import { Sidebar } from "@/components/sidebar"
import { VideoPlayer } from "@/components/video-player"
import { PlayerReport } from "@/components/player-report"
import { VideoGrid } from "@/components/video-grid"
import { getPlayerById, getHighlightsByPlayerId, getHighlightById } from "@/lib/data"
import { notFound } from "next/navigation"

interface PlayerPageProps {
  params: {
    id: string
  }
}

export default function PlayerPage({ params }: PlayerPageProps) {
  const player = getPlayerById(params.id)
  
  if (!player) {
    notFound()
  }

  const playerHighlights = getHighlightsByPlayerId(params.id)
  const featuredHighlight = playerHighlights[0] // Show first highlight as featured

  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-6 space-y-6">
            {/* Player Header */}
            <div className="space-y-2">
              <div className="flex items-center gap-4">
                <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center text-2xl font-bold">
                  {player.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <h1 className="text-3xl font-bold">{player.name}</h1>
                  <p className="text-lg text-muted-foreground">
                    {player.position} • {player.team} • {player.age} years old
                  </p>
                  <p className="text-sm text-muted-foreground">{player.nationality}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {/* Featured Video */}
                {featuredHighlight && (
                  <VideoPlayer
                    videoUrl={featuredHighlight.videoUrl}
                    title={featuredHighlight.title}
                    match={`${featuredHighlight.match} - ${new Date(featuredHighlight.date).toLocaleDateString()}`}
                    insights={[
                      {
                        type: featuredHighlight.type,
                        text: featuredHighlight.aiInsights.analysis,
                        timestamp: `${Math.floor(featuredHighlight.timestamp.start / 60)}:${(featuredHighlight.timestamp.start % 60).toString().padStart(2, '0')}`,
                      },
                    ]}
                  />
                )}

                {/* Related Highlights */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">
                    {player.name}'s Highlights ({playerHighlights.length})
                  </h2>
                  <VideoGrid />
                </div>
              </div>
              
              <div className="lg:col-span-1">
                <PlayerReport playerId={params.id} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
