"use client"

import { createContext, useContext, useState, ReactNode } from "react"

interface FilterState {
  selectedPlayer: string
  showStrengths: boolean
  showWeaknesses: boolean
  confidenceThreshold: number
  dateRange: "week" | "month" | "season" | "year" | "all"
  competition: string
  playbackSpeed: number
}

interface AppContextType {
  filters: FilterState
  setFilters: (filters: Partial<FilterState>) => void
  searchQuery: string
  setSearchQuery: (query: string) => void
}

const defaultFilters: FilterState = {
  selectedPlayer: "test-player",
  showStrengths: true,
  showWeaknesses: true,
  confidenceThreshold: 75,
  dateRange: "all",
  competition: "all",
  playbackSpeed: 1,
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [filters, setFiltersState] = useState<FilterState>(defaultFilters)
  const [searchQuery, setSearchQuery] = useState("")

  const setFilters = (newFilters: Partial<FilterState>) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }))
  }

  return (
    <AppContext.Provider value={{ filters, setFilters, searchQuery, setSearchQuery }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider")
  }
  return context
}
