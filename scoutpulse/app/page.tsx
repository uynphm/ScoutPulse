import { Navbar } from "@/components/navbar"
import { Sidebar } from "@/components/sidebar"
import { SearchSection } from "@/components/search-section"
import { VideoGrid } from "@/components/video-grid"
import { PlayerReport } from "@/components/player-report"

export default function Home() {
  return (
    <div className="flex h-screen flex-col">
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-6 space-y-6">
            <SearchSection />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <VideoGrid />
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
