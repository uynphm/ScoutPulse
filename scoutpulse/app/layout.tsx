import type React from "react"
import type { Metadata } from "next"
import { Suspense } from "react"
import { AppProvider } from "@/lib/context"
import "./globals.css"

export const metadata: Metadata = {
  title: "ScoutPulse - AI-Powered Soccer Scouting Platform",
  description: "Comprehensive soccer player analysis with video highlights and AI-driven insights",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans antialiased" suppressHydrationWarning={true}>
        <AppProvider>
          <Suspense fallback={null}>{children}</Suspense>
        </AppProvider>
      </body>
    </html>
  )
}
