import Link from "next/link"
import { Search, User, Settings, Upload } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function Navbar() {
  return (
    <header className="border-b border-border bg-card">
      <div className="flex h-16 items-center px-6 gap-4">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <span className="text-lg font-bold text-primary-foreground">SP</span>
          </div>
          <span className="text-xl font-bold text-foreground">ScoutPulse</span>
        </Link>

        <div className="flex-1 max-w-2xl mx-auto">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search for players, teams, or specific actions..."
              className="w-full pl-10 bg-background"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Link href="/upload">
            <Button variant="default" size="sm" className="gap-2">
              <Upload className="h-4 w-4" />
              Upload Video
            </Button>
          </Link>
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}
