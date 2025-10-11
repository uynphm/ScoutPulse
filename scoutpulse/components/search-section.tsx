import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"

export function SearchSection() {
  return (
    <div className="space-y-2">
      <h1 className="text-3xl font-bold text-balance">AI-Powered Player Analysis</h1>
      <p className="text-muted-foreground text-pretty">
        Search for any player action, strength, or weakness using natural language
      </p>

      <div className="relative mt-4">
        <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Try: 'Show Messi's best dribbles' or 'Find defensive weaknesses'..."
          className="w-full pl-12 h-14 text-lg bg-card"
        />
      </div>
    </div>
  )
}
