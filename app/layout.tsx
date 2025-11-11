import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'EKhu - Building Heating Load Calculator',
  description: 'AI Based Sustainable Building Planning - Heating Load Calculation and Simulation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: 'system-ui, -apple-system, sans-serif' }}>
        {children}
      </body>
    </html>
  )
}
