import { Navbar } from "@/components/navbar"
import { Sidebar } from "@/components/sidebar"
import { VideoPlayer } from "@/components/video-player"
import { PlayerReport } from "@/components/player-report"
import { VideoGrid } from "@/components/video-grid"

export default function PlayerPage() {
  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-6 space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <VideoPlayer
                  title="Exceptional Dribbling vs Real Madrid"
                  match="Barcelona vs Real Madrid - La Liga 2024"
                  insights={[
                    {
                      type: "strength",
                      text: "Perfect ball control under pressure",
                      timestamp: "0:15",
                    },
                    {
                      type: "strength",
                      text: "Quick change of direction",
                      timestamp: "0:32",
                    },
                  ]}
                />
                <div>
                  <h2 className="text-xl font-semibold mb-4">Related Highlights</h2>
                  <VideoGrid />
                </div>
              </div>
              <div className="lg:col-span-1">
                <PlayerReport />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
